#pragma once

struct _EXCEPTION_POINTERS;

// Writes build/last_run_report.json with status, rings, hardware
// state, and per-thread host stacks. Safe to call from:
//   - SEH unhandled-exception filter (pass fault_info)
//   - atexit handler (pass nullptr)
//   - debug_server TCP cmd (pass nullptr)
// Mutex-guarded; concurrent calls serialize.
extern "C" void psr_post_mortem_dump(const char* reason,
                                     struct _EXCEPTION_POINTERS* fault_info);
