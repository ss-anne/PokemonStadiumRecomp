/*
 * debug_server.h — TCP debug server interface for PokemonStadiumRecomp.
 * See src/main/debug_server.cpp for the command surface.
 */

#ifndef PKMNSTADIUM_DEBUG_SERVER_H
#define PKMNSTADIUM_DEBUG_SERVER_H

#include <atomic>
#include <cstdint>

namespace pkmnstadium {
namespace dbg {

// Lifecycle.
void start(int port = 4370);
void shutdown();

// Live state shared with the runner. Updated by the server in
// response to TCP commands; read by main.cpp's frame / input
// callbacks. Atomics so the server thread and game thread can
// touch them without a mutex.
extern std::atomic<bool>     g_fast_forward;
extern std::atomic<bool>     g_enable_instant_present_request;
extern std::atomic<uint64_t> g_vi_ticks;
extern std::atomic<uint64_t> g_frame_count;

extern std::atomic<bool>     g_input_override_active;
extern std::atomic<uint16_t> g_buttons_override;
extern std::atomic<int>      g_stick_x_override;
extern std::atomic<int>      g_stick_y_override;

} // namespace dbg
} // namespace pkmnstadium

#endif
