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

// Lifecycle. Default port 4371 (4370 is psxrecomp; one-port-per-recomp
// project keeps multiple debuggers attachable simultaneously).
void start(int port = 4371);
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

// Master audio volume, 0.0..1.0. Default 0 — overnight harness runs
// re-launch the runner repeatedly, and the boot/intro audio is rough
// to listen to in a loop. Override per-launch via PSR_VOLUME env var
// (e.g. PSR_VOLUME=0.5) or at runtime via TCP `set_volume {"value":x}`.
extern std::atomic<float>    g_audio_volume;

// Render-pipeline counters bumped by RT64Context.
// send_dl  = OSTask submissions (game asked RSP to process a display list).
// update_screen = VI swap (game asked the renderer to present a frame).
extern std::atomic<uint64_t> g_send_dl_count;
extern std::atomic<uint64_t> g_update_screen_count;
extern std::atomic<uint64_t> g_send_dl_audio_count;
extern std::atomic<uint64_t> g_send_dl_gfx_count;
extern std::atomic<uint64_t> g_send_dl_other_count;

} // namespace dbg
} // namespace pkmnstadium

#endif
