#!/bin/bash
# Reapply the fragment78 split to a freshly-checked-out disasm/ tree.
#
# The disasm/ submodule is intentionally never committed against by this
# project (per CLAUDE.md). The fragment78 split lives upstream-able as
# pret content but isn't merged yet, so we keep the diff here as a
# reproducible patch.
#
# Usage (from project root):
#   bash tools/_apply_disasm_fragment78_patch.sh
#
# What it does:
#   1. cd into disasm/, checks the working tree is clean (no other
#      stray edits to surprise)
#   2. applies tools/disasm_fragment78_split.patch
#   3. rebuilds the splat asm via WSL: cat yamls + splat split
#   4. runs the size-injector on fragment78.s
#   5. runs make to produce build/pokestadium-us.elf
#
# After this completes, run N64Recomp.exe game.toml from the project
# root, then ninja -C build to relink Stadium.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DISASM_DIR="${PROJECT_ROOT}/disasm"

if [[ ! -d "${DISASM_DIR}" ]]; then
    echo "ERROR: disasm/ not found at ${DISASM_DIR}" >&2
    exit 1
fi

cd "${DISASM_DIR}"

# Sanity: confirm we're on the expected pret state and there are no
# unrelated working-tree edits.
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERROR: disasm/ working tree has uncommitted edits — refusing to" >&2
    echo "       overwrite them. Inspect with 'git -C disasm status' and" >&2
    echo "       reset before running this script." >&2
    exit 1
fi

# Apply the patch.
git apply "${PROJECT_ROOT}/tools/disasm_fragment78_split.patch"
echo "[1/4] patch applied"

# Regenerate splat output (must use WSL — pret build chain doesn't run
# natively on Windows).
wsl -- bash -lc "cd /mnt/f/Projects/PokemonStadiumRecomp/disasm && \
    cat yamls/us/header.yaml yamls/us/rom.yaml > pokestadium-us.yaml && \
    rm -rf asm/us/fragments/78 asm/us/data/fragments/78 assets/us/fragments/78 && \
    .venv/bin/python3 -m splat split pokestadium-us.yaml > /tmp/splat_out.log 2>&1"
echo "[2/4] splat regen complete"

# Inject .size directives + dlabel rewriting in fragment78.s.
python3 "${PROJECT_ROOT}/tools/_inject_fragment78_sizes.py"
echo "[3/4] fragment78.s patched"

# Build via WSL.
wsl -- bash -lc "cd /mnt/f/Projects/PokemonStadiumRecomp/disasm && make"
echo "[4/4] disasm/build/pokestadium-us.elf built"

# Verify hash.
EXPECTED_MD5="ed1378bc12115f71209a77844965ba50"
ACTUAL_MD5="$(md5sum build/pokestadium-us.z64 | awk '{print $1}')"
if [[ "${ACTUAL_MD5}" != "${EXPECTED_MD5}" ]]; then
    echo "ERROR: built ROM hash ${ACTUAL_MD5} != expected ${EXPECTED_MD5}" >&2
    exit 1
fi
echo "ROM hash matches: ${ACTUAL_MD5}"
