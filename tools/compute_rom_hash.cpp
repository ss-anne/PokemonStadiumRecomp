// compute_rom_hash.cpp — print the XXH3_64bits hash of baserom.z64,
// matching librecomp's check_hash() in lib/N64ModernRuntime/librecomp/src/recomp.cpp.
// Build: clang-cl /std:c++20 compute_rom_hash.cpp /I ../lib/N64ModernRuntime/thirdparty/xxHash
// Usage: compute_rom_hash <path-to-rom>

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <vector>

#define XXH_INLINE_ALL
#include "xxhash.h"

int main(int argc, char** argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <rom>\n", argv[0]);
        return 1;
    }
    std::ifstream f(argv[1], std::ios::binary);
    if (!f) { fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
    f.seekg(0, std::ios::end);
    size_t sz = f.tellg();
    f.seekg(0);
    std::vector<uint8_t> data(sz);
    f.read(reinterpret_cast<char*>(data.data()), sz);
    uint64_t h = XXH3_64bits(data.data(), sz);
    printf("0x%016llXULL\n", (unsigned long long)h);
    return 0;
}
