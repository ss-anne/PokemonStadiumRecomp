# tools/

Project-specific tooling. General-purpose recompiler tooling lives
in `n64recomp/` (the engine).

## Inventory

*(empty — see "Removed" below.)*

## Planned

- `diff_state.py` — diff RDRAM snapshot against Ares oracle.
  Blocked on the Ares bridge (see `../ares-bridge/`).
- `dispatch_audit.py` — sweep generated C for every `LOOKUP_FUNC`
  call, ensure each lookup target is in `[[manual_funcs]]` or
  resolved via the ELF symbol table.
- `gb_tower_stub_audit.py` — verify all GB Tower entry points
  reachable from resident text are listed in `[[patches.stubs]]`.
- `byteswap.py` — convert `.v64` / `.n64` ROM dumps to native
  `.z64`. Standalone utility, no project state required.

## Removed

- `extract_overlays.py` — was scaffolded under the assumption
  that fragments collide in VRAM the way NES banks share
  `0x8000-0xFFFF`. Verified from `disasm/yamls/us/rom.yaml`
  that they don't (only 2 placeholder collisions out of 77
  fragments). The disasm's ELF carries every section's VA, so
  N64Recomp + Ghidra read it directly. If a real overlay-handling
  need surfaces later, recreate from the git history.

## Ground rules

- Tools here are **read-only against `disasm/`**. Never write to
  the submodule from tooling — only consume its files.
- Tools that touch `baserom.z64` must verify MD5 first.
- Tools that emit into gitignored directories (`generated/`,
  `build/`) must be **idempotent** — running twice on identical
  inputs produces byte-identical outputs.
- Tool output goes to gitignored directories or to stdout. Don't
  write into source-controlled paths from a script.
