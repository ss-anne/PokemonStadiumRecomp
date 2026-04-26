# DEBUG.md — Divergence triage protocol

How we identify, isolate, and fix divergences between the
recompiled output and the reference (pret build / Ares oracle / real
hardware).

## Layered oracles

1. **Static oracle — pret's rebuilt ROM.** `disasm` builds a
   byte-identical `pokestadium-us.z64` from sources. If our
   recompilation diverges from a behavior visible in the disasm,
   the disasm's C source is the answer. This is the *cheapest*
   oracle — no execution required.

2. **Dynamic oracle — Ares emulator.** For runtime behavior (state
   transitions, timing, RNG, RAM contents at frame N), Ares is the
   reference. The bridge is **not yet wired** — until it is, run
   Ares manually with the same inputs and diff state by hand.

3. **Real hardware.** Last-resort tiebreaker. Useful only for
   timing-sensitive issues (audio, raster effects).

## First-divergence rule

Always find the **first** divergence, not a downstream symptom.

- A black screen ten frames after boot is rarely a renderer bug.
  It's usually an earlier state divergence whose only visible
  manifestation is the blank frame.
- Walk back: latest known-good frame → first divergent frame →
  first divergent function call → first divergent register / mem
  store within that function.

## Triage tree

When the recompiled build misbehaves:

1. **Does the disasm build?** If not, the issue is upstream of us
   — fix in `disasm/` or upstream PR. Don't paper over.
2. **Does N64Recomp regen succeed without warnings?** Warnings
   from N64Recomp about unhandled relocations, missing symbols,
   or branch-target oddities are leading indicators.
3. **Is it in resident `text` or in a fragment?** Fragments are
   easier to isolate — recompile one fragment in isolation, run
   its entry point under a synthetic harness.
4. **Is it overlay-induced?** Two fragments at the same load VA
   conflict in our overlay handling? Re-check the overlay binding
   in `game.toml`.
5. **Is it GB-related?** If a symbol resolves into the GB Tower
   subsystem and we said it was stubbed, this is expected — extend
   the stub list in `game.toml`. If it's in resident `text` not
   actually called from GB, the stub list is over-broad.

## What NOT to do

- Don't add `if` guards in `extras.c` to skip the bug.
- Don't initialize a register to a magic constant in `generated/`
  to "fix" a downstream check.
- Don't stub in C — stub in `game.toml` so the stub is declared,
  diffable, and removable.
- Don't disable a watchdog assertion. If the watchdog fires, the
  state is wrong; fix the state.

## Tools (planned)

- `tools/extract_overlays.py` — fragment breakout. Status: TODO
  (skeleton present).
- `tools/diff_state.py` — diff RDRAM snapshot against Ares
  reference. Status: TODO (depends on oracle bridge).
- `tools/dispatch_audit.py` — verify all `jr ra` and `jr` indirect
  targets are covered by manual_funcs entries. Status: TODO.
- `tools/cycle_probe.c` — instruction-level cycle accumulator (port
  from segagenesisrecomp pattern if N64 timing matters). Status:
  not planned for first pass.

## Reverse-debug roadmap

NESRecomp's Tier 1–4 reverse debugger (Nestopia oracle bridge with
rewind / step / state delta) is the gold-standard model and is what
this project should grow toward. Sequencing:

- Tier 1: side-by-side console logging of executed function
  addresses (recomp vs Ares).
- Tier 2: per-function entry/exit register snapshots.
- Tier 3: per-frame RDRAM snapshot + diff.
- Tier 4: Ares-driven rewind to reproduce a divergence
  deterministically.

None of this exists yet. Track in `ISSUES.md`.
