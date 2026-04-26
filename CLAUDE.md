# CLAUDE.md — PokemonStadiumRecomp

Operational rules for AI-assisted work on this project. Defers to
the global `recompiler-discipline` skill for the cross-project
doctrine (no stubs, root-cause fixes in the recompiler over symptom
patches in generated C, regen + build + measure loop). This file
records project-specific decisions.

## Decisions of record

1. **Target ROM is US v1.0**, MD5 `ed1378bc12115f71209a77844965ba50`.
   Rev A (v1.1) is incompatible with pret's segment table. Always
   assert this hash before any operation that touches binary
   contents.

2. **Disasm is a git submodule at `disasm/`**, tracking
   `pret/pokestadium`. Treat its `yamls/us/rom.yaml` as the
   single source of truth for segment boundaries.

3. **Engine is N64Recomp**, vendored at `n64recomp/` (clone or
   junction to `../N64Recomp`). SHA pinned in `n64recomp.pin`. CMake
   asserts pin at configure time.

4. **GB Tower is out of scope for the first playable build.** Stub
   entry points; do not attempt to port the embedded GB emulator.
   When you encounter symbols `gb_tower`, `gb_mbc`, or anything in
   `gb_tower_roms`, route to a stub.

5. **Oracle is Ares** (chosen for accuracy). The bridge is not
   wired yet. Until it is, divergence checking happens by manual
   side-by-side runs against Ares; do not invent a fake oracle to
   make tests pass.

6. **No per-fragment overlay extraction.** Pokemon Stadium's 77
   fragments mostly have unique VRAM addresses (verified from
   rom.yaml), so the NES-style bank-extraction pattern doesn't
   apply. N64Recomp and Ghidra both read the post-build ELF
   directly. The 2 placeholder VRAM collisions
   (`0x8FC00000`, `0x88920000`) get handled in `game.toml` only
   if they cause actual analysis problems.

## Workflow rules

- **Never edit `generated/`.** It is recompiler output. Fix the
  root cause in `game.toml` or upstream in `n64recomp/`, then
  regen.
- **Never edit `disasm/`** (submodule). To change pret content,
  upstream a PR or fork; do not commit local edits.
- **Always verify hashes** before recompiling: `baserom.z64`
  against the expected MD5, and `n64recomp/` HEAD against the pin.
- **Do not stub functions in generated C** to make builds pass.
  If you need a stub, declare it in `game.toml` under
  `[[patches.stubs]]` so it lives in config, not in output.
- **Mod loader work is deferred** — see proposal P3/P4/P5 in
  `../_personal-notes/n64recomp-eval/N64RECOMP_PROPOSALS.md`.
  Do not scaffold mod tooling until the base game runs.

## Reading order for a new contributor

1. `README.md` — what this project is and the layout.
2. `disasm/README.md` and `disasm/yamls/us/rom.yaml` — the truth
   about the binary.
3. `n64recomp/README.md` — the engine.
4. `DEBUG.md` — how divergence is identified and triaged.
5. This file.

## When you don't know what to do

Default to **understanding before action**. Read the segment in
`rom.yaml`, look up the address in Ghidra (when configured), check
whether the disasm has it C-decompiled or still in `asm/`. Only
then propose a recompiler change. The cost of a wrong patch in
`game.toml` is low; the cost of a wrong workaround in `extras.c`
that masks a bug elsewhere is high.
