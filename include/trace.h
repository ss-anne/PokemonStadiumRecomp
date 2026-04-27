/*
 * trace.h — TRACE_ENTRY / TRACE_RETURN hooks for trace_mode = true.
 *
 * N64Recomp's recompiler emits literal `TRACE_ENTRY()` and
 * `TRACE_RETURN()` at the start/end of every recompiled function
 * when game.toml has `trace_mode = true`. The header is auto-
 * included into every generated funcs_N.c via config.recomp_include.
 *
 * These hooks push (function_name) into a lock-free ring buffer
 * exposed via the TCP debug server's `trace_recent` command. Lets
 * us see — without modifying the engine or generated output —
 * exactly which game functions are executing right now. Critical
 * for finding "where is the boot stuck?" without random trial
 * fixes.
 *
 * Per project principles (PRINCIPLES.md #12): not stubs. Real
 * function calls into a real ring writer; the recorded data is
 * used for diagnosis, not for simulating behavior.
 */

#ifndef PKMNSTADIUM_TRACE_H
#define PKMNSTADIUM_TRACE_H

#ifdef __cplusplus
extern "C" {
#endif

void pkmnstadium_trace_entry(const char *func);
void pkmnstadium_trace_return(const char *func);

#ifdef __cplusplus
}
#endif

// Engine emits these as bare `TRACE_ENTRY()` / `TRACE_RETURN()`
// without a trailing `;` — bake the terminator into the macro
// so each expansion is a complete statement on its own. (do/while(0)
// would still need an outer `;`.) Trailing `;` is fine even if
// the engine ever does emit one — `;;` is a valid empty statement.
#define TRACE_ENTRY()  pkmnstadium_trace_entry(__func__);
#define TRACE_RETURN() pkmnstadium_trace_return(__func__);

#endif
