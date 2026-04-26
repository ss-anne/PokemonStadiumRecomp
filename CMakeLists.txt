cmake_minimum_required(VERSION 3.20)
project(PokemonStadiumRecomp C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---- ROM hash check ---------------------------------------------------------
set(EXPECTED_BASEROM_MD5 "ed1378bc12115f71209a77844965ba50")
if(EXISTS "${CMAKE_SOURCE_DIR}/baserom.z64")
    file(MD5 "${CMAKE_SOURCE_DIR}/baserom.z64" ACTUAL_BASEROM_MD5)
    if(NOT ACTUAL_BASEROM_MD5 STREQUAL EXPECTED_BASEROM_MD5)
        message(WARNING
            "baserom.z64 MD5 mismatch.\n"
            "  expected: ${EXPECTED_BASEROM_MD5}  (US v1.0)\n"
            "  actual:   ${ACTUAL_BASEROM_MD5}")
    else()
        message(STATUS "baserom.z64 MD5 OK (US v1.0)")
    endif()
endif()

# ---- N64ModernRuntime (junctioned at lib/N64ModernRuntime) -----------------
# Provides ultramodern (libultra/N64-OS shim) and librecomp (recompiler
# runtime: ai/dp/sp/vi/cont/heap/etc). The N64Recomp engine submodule
# inside is itself junctioned to F:/Projects/N64Recomp on the
# pokestadium-integration branch.
add_subdirectory(${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime)

# ---- Collect generated function files ---------------------------------------
file(GLOB GENERATED_FUNCS_FILES "${CMAKE_SOURCE_DIR}/generated/funcs_*.c")
list(LENGTH GENERATED_FUNCS_FILES GENERATED_COUNT)
message(STATUS "Generated funcs files: ${GENERATED_COUNT}")

# ---- Runner executable ------------------------------------------------------
add_executable(PokemonStadiumRecomp
    ${GENERATED_FUNCS_FILES}
    extras.c
    runner_main.cpp
)

# Generated C calls libultra functions (e.g. __osPiGetAccess_recomp)
# defined in librecomp without forward-declaring them — N64Recomp
# emits the call sites but doesn't generate decls. The linker
# resolves them. Suppress the implicit-decl error to a warning.
set_source_files_properties(${GENERATED_FUNCS_FILES} PROPERTIES
    COMPILE_FLAGS "-Wno-implicit-function-declaration")

target_include_directories(PokemonStadiumRecomp PRIVATE
    ${CMAKE_SOURCE_DIR}/generated
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/librecomp/include
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/ultramodern/include
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/N64Recomp/include
)

target_link_libraries(PokemonStadiumRecomp PRIVATE
    librecomp
    ultramodern
)

if(WIN32)
    target_link_libraries(PokemonStadiumRecomp PRIVATE Winmm.lib)
endif()
