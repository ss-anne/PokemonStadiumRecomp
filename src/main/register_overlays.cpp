/*
 * register_overlays.cpp — feed the generated section/overlay table
 * into librecomp's recomp::overlays::register_overlays().
 *
 * Adapted from Zelda64Recomp's src/main/register_overlays.cpp. The
 * generated/recomp_overlays.inl defines:
 *   SectionTableEntry section_table[]      (every code section)
 *   uint16_t          overlay_sections_by_index[]  (overlay slots)
 *   size_t            num_sections          (total sections)
 *
 * Without this registration, librecomp's func_map stays empty for
 * every section beyond patches — so any LOOKUP_FUNC at runtime fails
 * with "Failed to find function at 0x...". This is the missing piece
 * that lets the resident kernel + 77 fragments resolve at runtime.
 */

#include <cstdint>
#include <cstddef>

#include "librecomp/overlays.hpp"

#define ARRLEN(x) (sizeof(x) / sizeof((x)[0]))

#include "../../generated/recomp_overlays.inl"

namespace pokestadium {
    void register_overlays();
}

void pokestadium::register_overlays() {
    recomp::overlays::overlay_section_table_data_t sections {
        .code_sections     = section_table,
        .num_code_sections = ARRLEN(section_table),
        .total_num_sections = num_sections,
    };

    recomp::overlays::overlays_by_index_t overlays {
        .table = overlay_sections_by_index,
        .len   = ARRLEN(overlay_sections_by_index),
    };

    recomp::overlays::register_overlays(sections, overlays);
}
