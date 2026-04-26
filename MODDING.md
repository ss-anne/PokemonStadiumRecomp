# MODDING — PokemonStadiumRecomp

> **Status: deferred.** Modding is intentionally out of scope until
> the base game boots and is playable. This file is a placeholder so
> the slot is reserved and the design doesn't drift.

## Design intent (when we get to it)

Modding will follow the N64Recomp four-tool pattern: mod manifest
schema (`mod.json`), RecompModTool (mod ELF → symbol tables),
OfflineModRecomp (mod recompiler), RecompModMerger (multi-mod
conflict resolution).

Until then, **no patches will be exposed as mod hooks**. All
behavioral changes go through `game.toml` (declared, diffable,
versioned with the project) — not through a runtime mod system that
isn't designed yet.

## Hard rules to preserve mod-friendliness later

Even before there's a mod system, decisions made now can either
help or hinder one later. Rules:

- **Don't bake game-specific assumptions into engine glue.**
  Anything that looks like "Pokémon Stadium specifically does X"
  belongs in `extras.c` or `game.toml`, never in `n64recomp/`.
- **Keep `extras.c` symbols namespaced.** Once mods exist, two
  mods can't both override `update_player_state`. Prefix
  game-specific overrides with `pkmnstadium_` or similar so the
  mod loader can disambiguate.
- **Keep generated output deterministic.** A mod system reasons
  about diffs against a baseline; if regen produces gratuitously
  different output run-to-run, the mod tooling can't work.

## When mods come online

Open this file, port the schema from
`N64Recomp/RecompModTool/main.cpp:25-41`, and follow the same
sequencing: manifest → RecompModTool analogue → ModMerger.
