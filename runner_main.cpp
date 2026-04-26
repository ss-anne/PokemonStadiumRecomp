// runner_main.cpp — minimal entry for PokemonStadiumRecomp.
//
// First-pass goal: just LINK. Calling into librecomp/ultramodern
// requires graphics/audio/input wiring that we don't have yet; for
// now this just confirms the recompiled C compiles + the runtime
// libraries link. When you run the resulting exe it'll print the
// status and exit; full boot needs a renderer + scheduler set up.

#include <cstdio>
#include <cstdlib>

extern "C" {

int main(int argc, char **argv) {
    std::printf("PokemonStadiumRecomp — link-only entry.\n");
    std::printf("  generated funcs: linked\n");
    std::printf("  librecomp / ultramodern: linked\n");
    std::printf("Full runner (renderer + scheduler + boot) not wired yet.\n");
    return 0;
}

} // extern "C"
