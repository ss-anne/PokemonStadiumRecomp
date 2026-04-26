cmake_minimum_required(VERSION 3.20)
project(PokemonStadiumRecomp C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

set(N64RECOMP_ROOT ${CMAKE_SOURCE_DIR}/n64recomp)

# ---- n64recomp pin check ----------------------------------------------------
# n64recomp/ is a directory junction (Windows) or symlink (Unix) to a central
# checkout, OR a fresh clone created by setup.bat/sh. n64recomp.pin records the
# expected SHA. Configure-time check fails fast on drift.
#
# Two optional fields in n64recomp.pin:
#   branch = <ref>   default origin/main, used when sha is unset
#   sha    = <sha>   exact pin, takes precedence

if(EXISTS "${CMAKE_SOURCE_DIR}/n64recomp.pin")
    file(STRINGS "${CMAKE_SOURCE_DIR}/n64recomp.pin" _PIN_LINES)
    set(N64RECOMP_PIN_BRANCH "")
    set(N64RECOMP_PIN_SHA "")
    foreach(_line IN LISTS _PIN_LINES)
        if(_line MATCHES "^[ \t]*#")
            # comment, skip
        elseif(_line MATCHES "^[ \t]*branch[ \t]*=[ \t]*(.*)$")
            string(STRIP "${CMAKE_MATCH_1}" N64RECOMP_PIN_BRANCH)
        elseif(_line MATCHES "^[ \t]*sha[ \t]*=[ \t]*(.*)$")
            string(STRIP "${CMAKE_MATCH_1}" N64RECOMP_PIN_SHA)
        endif()
    endforeach()

    if(N64RECOMP_PIN_SHA)
        set(N64RECOMP_EXPECTED_SHA "${N64RECOMP_PIN_SHA}")
        set(N64RECOMP_PIN_SOURCE "explicit sha in n64recomp.pin")
    else()
        if(NOT N64RECOMP_PIN_BRANCH)
            set(N64RECOMP_PIN_BRANCH "origin/main")
        endif()
        execute_process(
            COMMAND git -C "${N64RECOMP_ROOT}" rev-parse "${N64RECOMP_PIN_BRANCH}"
            OUTPUT_VARIABLE N64RECOMP_EXPECTED_SHA
            OUTPUT_STRIP_TRAILING_WHITESPACE
            RESULT_VARIABLE _N64RECOMP_RP_RC
        )
        if(NOT _N64RECOMP_RP_RC EQUAL 0)
            message(WARNING
                "n64recomp pin: failed to resolve branch '${N64RECOMP_PIN_BRANCH}' "
                "in ${N64RECOMP_ROOT}. Run setup.sh / setup.bat first.")
            return()
        endif()
        set(N64RECOMP_PIN_SOURCE "tip of ${N64RECOMP_PIN_BRANCH}")
    endif()

    if(EXISTS "${N64RECOMP_ROOT}/.git" OR IS_DIRECTORY "${N64RECOMP_ROOT}")
        execute_process(
            COMMAND git -C "${N64RECOMP_ROOT}" rev-parse HEAD
            OUTPUT_VARIABLE N64RECOMP_ACTUAL_SHA
            OUTPUT_STRIP_TRAILING_WHITESPACE
            RESULT_VARIABLE _N64RECOMP_HEAD_RC
        )
        if(_N64RECOMP_HEAD_RC EQUAL 0
           AND NOT N64RECOMP_ACTUAL_SHA STREQUAL N64RECOMP_EXPECTED_SHA)
            message(WARNING
                "n64recomp pin mismatch.\n"
                "  expected: ${N64RECOMP_EXPECTED_SHA}  (from ${N64RECOMP_PIN_SOURCE})\n"
                "  actual:   ${N64RECOMP_ACTUAL_SHA}  (HEAD of ${N64RECOMP_ROOT})\n"
                "Run: git -C ${N64RECOMP_ROOT} checkout ${N64RECOMP_EXPECTED_SHA}\n"
                "Or roll forward: edit ${CMAKE_SOURCE_DIR}/n64recomp.pin "
                "(set sha=${N64RECOMP_ACTUAL_SHA}).")
        elseif(_N64RECOMP_HEAD_RC EQUAL 0)
            message(STATUS "n64recomp pin OK: ${N64RECOMP_EXPECTED_SHA} (${N64RECOMP_PIN_SOURCE})")
        endif()
    endif()
endif()

# ---- ROM hash check ---------------------------------------------------------
set(EXPECTED_BASEROM_MD5 "ed1378bc12115f71209a77844965ba50")

if(EXISTS "${CMAKE_SOURCE_DIR}/baserom.z64")
    file(MD5 "${CMAKE_SOURCE_DIR}/baserom.z64" ACTUAL_BASEROM_MD5)
    if(NOT ACTUAL_BASEROM_MD5 STREQUAL EXPECTED_BASEROM_MD5)
        message(WARNING
            "baserom.z64 MD5 mismatch.\n"
            "  expected: ${EXPECTED_BASEROM_MD5}  (US v1.0)\n"
            "  actual:   ${ACTUAL_BASEROM_MD5}\n"
            "Rev A (v1.1) is incompatible with pret's segment table.")
    else()
        message(STATUS "baserom.z64 MD5 OK (US v1.0)")
    endif()
else()
    message(WARNING "baserom.z64 not present; recompile target will be unbuildable.")
endif()

# ---- Targets (placeholders) -------------------------------------------------
# The runner target is intentionally not declared yet — it depends on
# N64ModernRuntime, which is not vendored at this stage. See ISSUES.md.
#
# What goes here once the runtime is wired:
#
#   add_executable(PokemonStadiumRecomp
#       generated/pokestadium_full.c
#       generated/pokestadium_dispatch.c
#       extras.c
#       n64_snapshot.c
#       verify_mode.c
#       watchdog.c
#       ${RUNTIME_SOURCES}
#   )
#   target_link_libraries(PokemonStadiumRecomp PRIVATE N64ModernRuntime SDL2)
#
# A custom command can then drive regen:
#   add_custom_command(OUTPUT generated/pokestadium_full.c
#       COMMAND $<TARGET_FILE:N64RecompCLI> ${CMAKE_SOURCE_DIR}/game.toml
#       DEPENDS game.toml baserom.z64 N64RecompCLI)

# ---- Diagnostic summary -----------------------------------------------------
message(STATUS "PokemonStadiumRecomp: scaffold-only configure complete.")
message(STATUS "  Disasm submodule:    ${CMAKE_SOURCE_DIR}/disasm")
message(STATUS "  N64Recomp engine:    ${N64RECOMP_ROOT}")
message(STATUS "  Next: implement tools/extract_overlays.py + seed game.toml.")
