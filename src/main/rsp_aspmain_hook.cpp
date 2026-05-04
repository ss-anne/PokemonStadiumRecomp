/*
 * rsp_aspmain_hook.cpp — Pre-task hook for Pokemon Stadium's aspMain.
 *
 * Stadium's aspMain (ROM 0x68020, 0xC60 bytes) is a stripped variant
 * of the standard libultra audio microcode. Unlike Zelda64's aspMain
 * (which calls a setup function at PC 0x1058 to load the audio
 * command list before dispatch), Stadium's entry path
 *   PC 0x1000 (mfc0 DPC_STATUS) → L_102C (jal L_1120)
 * has NO command-load step. It depends on rspboot leaving:
 *   - $29 = 0x2B0  (DMEM offset of audio command list)
 *   - $30 > 0      (chunk-remaining counter)
 *   - SP_MEM_ADDR / SP_DRAM_ADDR / SP_RD_LEN already pointing at a
 *     safe RDRAM range so the L_1120 → L_10EC tail-DMA is a no-op
 *   - DMEM[0x2B0..0x3EF] = first chunk of audio commands
 *
 * Our HLE doesn't run rspboot, so the recompiled aspMain hits the
 * dispatch loop at L_1048 with $29 = 0 and dispatch table residue
 * in DMEM. The first L_10EC tail-DMA writes 1 byte from RDRAM[0]
 * into DMEM[3], corrupting dispatch[0]'s low byte from 0x10 to 0x00,
 * which makes the dispatch lookup return 0xEC, which dispatches to
 * L_10EC again → self-perpetuating infinite loop (caught by the
 * RSPRecomp watchdog after 100M transitions).
 *
 * This hook replicates the rspboot residue Stadium's aspMain
 * expects:
 *   1. DMA the first chunk of audio commands (up to 0x140 bytes)
 *      from task->t.data_ptr to DMEM[0x2B0].
 *   2. Seed $29, $30, $27, $28 to match what the dead-code init
 *      function at PC 0x10A0 would have computed if Stadium's
 *      boot path had called it.
 *   3. Seed dma_mem_address / dma_dram_address / r3 so the boot
 *      path's bogus L_1120 → L_10EC DMA at PC 0x1140 becomes a
 *      no-op (re-reads ucode_data byte 0 into DMEM[0xFFC], which
 *      is safe scratch space outside the dispatch table).
 *
 * Validation: with this hook, the watchdog should NOT trip; dispatch
 * should land on real handlers (0x139C, 0x119C, etc.) and aspMain
 * should reach the `mtc0 r1, SP_STATUS; break 0` at L_108C in finite
 * time, returning RspExitReason::Broke.
 *
 * Per project principles (PRINCIPLES.md #12): this is NOT a stub. It
 * encodes the real HLE-correct boot residue Stadium's aspMain needs.
 * On real hardware rspboot does the equivalent setup; we replicate it.
 */

#include <cstdint>
#include <cstdio>
#include <cstring>

#include "librecomp/rsp.hpp"
#include "ultramodern/ultra64.h"

// Reach into librecomp's DMEM array. Declared at file scope (not
// inside our namespace) so the extern resolves to the global
// `dmem` defined in librecomp/src/rsp.cpp.
extern uint8_t dmem[];

namespace pokestadium::rsp {

// Audio task command-list chunk size. Stadium's dead-code init at
// PC 0x10A0 caps the initial DMA at 0x140 bytes; this matches what
// the dispatch loop's "refresh" path expects.
constexpr uint32_t kAudioChunkSize = 0x140;

// DMEM destination offset where audio commands live. Stadium's
// dead-code init function tail (`addi $29, $0, 0x2B0`) puts them
// here; the dispatch loop reads commands via `lw $26, 0($29)`.
constexpr uint32_t kAudioCommandsDmemOffset = 0x2B0;

// Safe DMEM scratch offset for the boot-path's bogus L_10EC DMA.
// Anywhere past the dispatch table (0x00..0x1F) and the constants
// area (0x20..0xAF) and the audio commands (0x2B0..0x3EF) works.
// 0xFFC is just before the OSTask copy at 0xFC0 — wait, 0xFC0 is
// where OSTask starts. Use 0xFA0 instead, which is set up as r24
// in the boot path and is documented scratch.
constexpr uint32_t kBootDmaSafeDmemOffset = 0xFA0;

void aspmain_pre_task(uint8_t* rdram,
                      ::RspContext* ctx,
                      const char* ucode_name,
                      uint32_t ucode_addr) {
    // Read OSTask back from DMEM[0xFC0] where the runtime stored
    // it. We could pass a separate OSTask* but reading from DMEM
    // matches what real rspboot does: the task struct lives there
    // and aspMain reads its own data_ptr / data_size from
    // DMEM[0xFC0+0x30] / DMEM[0xFC0+0x34].
    //
    // Pull values directly from the runtime-side dmem array via
    // the same XOR-3 byte ordering the recompiled MEM_W_LOAD uses.
    // We need data_ptr (offset 0x30) and data_size (offset 0x34).
    auto load_w = [](uint32_t off) -> uint32_t {
        // Replicate RSP_MEM_W_LOAD: read 4 bytes with each byte
        // XOR-3'd to host position (i^3). On LE host the result
        // is the big-endian word as a native uint32.
        uint32_t out = 0;
        for (int i = 0; i < 4; i++) {
            uint8_t b = dmem[(off + i) ^ 3];
            reinterpret_cast<uint8_t*>(&out)[i ^ 3] = b;
        }
        return out;
    };
    uint32_t data_ptr  = load_w(0xFC0 + 0x30);
    uint32_t data_size = load_w(0xFC0 + 0x34);

    if (data_size == 0 || data_ptr == 0) {
        // Empty task — let aspMain handle whatever degenerate
        // state it falls into. Don't synthesize fake commands.
        return;
    }

    // Compute first chunk size (matches dead-code init at 0x10A0).
    uint32_t chunk = (data_size > kAudioChunkSize)
                         ? kAudioChunkSize
                         : data_size;

    // Pre-load first chunk of audio commands. dma_rdram_to_dmem
    // takes rd_len as inclusive (RSP DMA semantics: the value
    // written to SP_RD_LEN equals length-1).
    ::recomp::rsp::dma_rdram_to_dmem_external(
        rdram,
        kAudioCommandsDmemOffset,
        data_ptr,
        chunk - 1);

    // Seed registers as if the dead-code init function had run:
    //   $29 = 0x2B0    (commands DMEM ptr)
    //   $30 = chunk    (chunk byte count remaining; dispatch uses
    //                   `bgtz $30` to decide if the current DMEM
    //                   chunk has more commands or needs refresh)
    //   $27 = data_size - chunk  (DRAM bytes remaining)
    //   $28 = data_ptr + chunk   (next DRAM read addr)
    //
    // Note: aspMain's entry path also reads r28/r27 from DMEM
    // OSTask fields at PC 0x1004/0x1008, so it'll OVERWRITE our
    // r28/r27 seeds. That's fine — the original boot path's
    // r28=data_ptr, r27=data_size leads to the L_106C refresh
    // path picking up where we left off (it advances r28 by chunk
    // size in jal-L_1120 calls, decrements r27, etc.). The KEY
    // seeds the boot path doesn't overwrite are r29 and r30.
    ctx->r29 = kAudioCommandsDmemOffset;
    ctx->r30 = static_cast<int32_t>(chunk);
    ctx->r27 = data_size - chunk;
    ctx->r28 = data_ptr + chunk;

    // Seed DMA-engine residue + r3 + r31 to match what real rspboot
    // leaves behind, per Ares oracle measurement at first L_10EC of
    // a Stadium audio task (queried via tools/diff_aspmain.py +
    // ares_oracle_server's boot snapshot):
    //
    //   dma_mem_address  = 0x2B0  (DMEM of audio command region)
    //   dma_dram_address = data_ptr + chunk  (next chunk's DRAM addr)
    //   r3               = chunk - 1 = 0x13F (size-1 of just-loaded chunk)
    //   r31              = 0x1144  (boot-path return point for L_10EC's jr)
    //
    // The boot-path L_10EC at PC 0x10EC fires `mtc0 r3, SP_RD_LEN` in
    // its delay slot; that kicks a DMA of (r3+1) bytes from
    // SP_DRAM_ADDR to SP_MEM_ADDR. With the values above, that DMA
    // refills DMEM[0x2B0..0x3EF] with the FIRST already-resident
    // chunk over itself (no-op effectively) — but importantly, the
    // post-DMA auto-increment moves SP_MEM_ADDR to 0x3F0 and
    // SP_DRAM_ADDR forward by 0x140, lining up the NEXT chunk for
    // the dispatcher's eventual L_106C -> L_1120 -> L_10EC refresh.
    //
    // r31 = 0x1144 is the address of the instruction immediately
    // after `j 0x10EC`'s delay slot at PC 0x1140 inside L_1120. After
    // L_10EC's `jr r31`, control resumes at 0x1144 to continue the
    // boot setup (which leads into the dispatch loop via L_106C's
    // bgtz r30 path). Without this, jr r31 returns to whatever the
    // last jal set (0x1038 — the dispatch loop start), which causes
    // the dispatcher to re-enter L_10EC every iteration.
    ctx->dma_mem_address  = kAudioCommandsDmemOffset;
    ctx->dma_dram_address = data_ptr + chunk;
    ctx->r3               = chunk - 1;
    ctx->r31              = 0x1144;

    // Inform diagnostic ring that the hook ran. Quiet; not an
    // error path. Helpful if a future regression makes us doubt
    // whether the hook was even invoked.
    fprintf(stderr,
        "[aspmain_hook] %s: data_ptr=0x%08X data_size=0x%X chunk=0x%X "
        "→ DMEM[0x%X], r29=0x2B0, r30=%u\n",
        ucode_name ? ucode_name : "?",
        data_ptr, data_size, chunk,
        kAudioCommandsDmemOffset, chunk);
    fflush(stderr);
}

void register_pre_task_hooks() {
    ::recomp::rsp::set_pre_task_hook("aspMain", aspmain_pre_task);
}

}  // namespace pokestadium::rsp
