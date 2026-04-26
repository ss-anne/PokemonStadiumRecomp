# Open issues — PokemonStadiumRecomp

Living list of known gaps. Use this as a pre-flight before starting
a new work session.

## Scaffolding (current phase)

- [ ] Replace placeholder SHA in `n64recomp.pin` with the real
      40-char HEAD of `../N64Recomp` after `setup.sh` runs. Currently
      pinned to a placeholder padded with hex.
- [ ] Verify `setup.sh` and `setup.bat` end-to-end on a clean clone.
- [ ] First `disasm/make init` + `disasm/make` run — confirm pret
      builds identically against `disasm/baseroms/us/baserom.z64`.

## Recompilation pipeline (next phase)

- [ ] **Build pret's disasm to produce `pokestadium-us.elf`.**
      Requires MIPS binutils + make + python. On Windows this
      means WSL2 — full instructions in `docs/disasm-build.md`.
- [ ] Wire `game.toml` to point at the produced ELF
      (`disasm/build/us/pokestadium.elf`).
- [ ] First N64Recomp run against the ELF. Expect warnings on
      indirect call sites and unmapped relocations — triage them.
- [ ] CMake target that invokes `N64RecompCLI` and depends on
      the disasm build.
- [ ] Decide what to do with the 2 placeholder-VRAM fragment
      collisions (`0x8FC00000`, `0x88920000`) — likely nothing
      until they cause an analysis or recomp warning.

## Runtime (depends on N64ModernRuntime)

- [ ] Vendor or submodule N64ModernRuntime (the runtime that
      Zelda64Recomp / MM:R consume).
- [ ] Wire the runner CMake target — link `generated/*.c` against
      runtime + SDL2.
- [ ] First boot — expect to crash or blackscreen; record the
      first divergence.

## GB Tower (out of scope, first pass)

- [ ] Enumerate all GB-related entry points reachable from
      resident `text`. Symbols of interest: `gb_tower`, `gb_mbc`,
      addresses near `0xB230`, `0xE1C0`, `0xE570`.
- [ ] Add `[[patches.stubs]]` entries in `game.toml` for each.
- [ ] Confirm main game (battles, minigames) reachable without
      hitting any stub.

## Oracle / divergence checking

The Ares oracle bridge lives in the **engine**, not in this
project — see `n64recomp/ares-bridge/` and its
`README.md` / `DESIGN.md`. PokemonStadiumRecomp consumes the
bridge as a CMake target.

Engine-side work (tracked on the `pokestadium-integration` branch
of N64Recomp):
- [ ] Carve out a buildable, headless Ares N64 core
      (`ares-bridge` Phase 1).
- [ ] Implement lifecycle + state read + step
      (Phases 2-4).
- [ ] Validate the bridge against Zelda64Recomp running OoT
      (Phase 5) **before** turning it on for this project.

Consumer-side work (this project):
- [ ] Wire `target_link_libraries(PokemonStadiumRecomp PRIVATE
      ares_bridge)` in CMakeLists.txt once the runner target
      exists.
- [ ] `verify_mode.c/h` — runtime mode that boots, runs N frames,
      diffs state via `ares_read_*`, exits. Pattern matches
      Faxanadu's `verify_mode.c` against Nestopia.
- [ ] `n64_snapshot.c/h` — local snapshot format. Layout chosen
      to match the byte order Ares returns from
      `ares_read_memory()`.
- [ ] `watchdog.c/h` — divergence assertion firing on register
      or memory mismatch reported by the bridge.

## Modding (deferred — see proposals)

Explicitly **not** prioritized until the base game boots and is
playable.

- [ ] Mod manifest schema.
- [ ] RecompModTool / OfflineModRecomp integration.
- [ ] RecompModMerger.
- [ ] LiveRecomp / sljit JIT — almost certainly skipped.

## Documentation

- [ ] `MODDING.md` — flesh out post-MVP. Currently a placeholder.
- [ ] `docs/` — design notes on overlay handling, GB Tower
      stubbing, oracle architecture.
- [ ] Per-overlay README skeletons under `overlays/<name>/` once
      extraction tool runs.
