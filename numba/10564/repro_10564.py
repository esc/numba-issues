#!/usr/bin/env python
"""
Reproducer harness for numba/numba#10564:
    `TimingListener` may not be thread-safe

Race we're targeting (numba.core.event.TimingListener):

    def on_start(self, event):
        if self._depth == 0:
            self._ts = timer()
        self._depth += 1

    def on_end(self, event):
        self._depth -= 1
        if self._depth == 0:
            last = getattr(self, "_duration", 0)
            self._duration = (timer() - self._ts) + last

`_depth` is mutated with non-atomic +=/-=, and `_ts` is written under a
depth==0 guard. Two threads that both observe `_depth == 0` in `on_start`
will both set `_ts`, but a lost-update on `_depth += 1` can leave the
counter at 1 instead of 2. The next `on_end` then drops it to 0 while
another thread is still inside its compile, and a subsequent `on_start`
that observes `_depth != 0` (because the counter is now skewed) will not
re-set `_ts` -- so when `on_end` later drops to 0 and reads `self._ts`,
the attribute may have been deleted, never set, or stale.

This script drives that path two ways:

    --mode=direct   pure event-API stress (no compile, fastest)
    --mode=compile  many distinct @jit kernels compiled in parallel
    --mode=both     run both back to back

Usage examples:

    python repro_10564.py
    python repro_10564.py --mode=compile -t 64 -n 200
    PYTHON_GIL=0 python3.14t repro_10564.py -t 64 -n 20000

Exit code: 0 = no failures observed (race may still be latent),
           1 = at least one failure reproduced.
"""

from __future__ import annotations

import argparse
import os
import sys
import sysconfig
import threading
import time
import traceback
from typing import Callable, NamedTuple

import numba
from numba.core import event as nb_event


# ---------------------------------------------------------------- env info ----

def gil_enabled() -> bool:
    """True if the GIL is currently enabled in this interpreter."""
    probe = getattr(sys, "_is_gil_enabled", None)
    return True if probe is None else bool(probe())


def is_freethreaded_build() -> bool:
    return bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


def banner() -> None:
    uname_release = getattr(os, "uname", lambda: None)
    rel = uname_release().release if callable(uname_release) else "n/a"
    print("=" * 72)
    print(f"Python              : {sys.version.split()[0]}  ({sys.executable})")
    print(f"Free-threaded build : {is_freethreaded_build()}")
    print(f"GIL enabled now     : {gil_enabled()}")
    print(f"Numba               : {numba.__version__}")
    print(f"Platform / kernel   : {sys.platform} / {rel}")
    print(f"CPU count           : {os.cpu_count()}")
    print("=" * 72)


# ---------------------------------------------------------------- failures ----

class Failure(NamedTuple):
    mode: str
    tid: int
    iteration: int
    tb: str


def collect_failures(
    fn: Callable[[int, int, list[Failure], threading.Lock], None],
    nthreads: int,
    iterations: int,
    label: str,
) -> list[Failure]:
    """Run `fn(tid, iterations, failures, lock)` in `nthreads` threads."""
    failures: list[Failure] = []
    flock = threading.Lock()
    barrier = threading.Barrier(nthreads)

    def runner(tid: int) -> None:
        barrier.wait()  # all threads released ~simultaneously
        fn(tid, iterations, failures, flock)

    threads = [threading.Thread(target=runner, args=(i,), daemon=True,
                                name=f"{label}-{i}")
               for i in range(nthreads)]
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    dt = time.perf_counter() - t0
    print(f"[{label}] {nthreads} threads x {iterations} iters in {dt:.2f}s")
    return failures


# ----------------------------------------------------------------- direct ----

EVENT_KIND = "repro_10564"


def run_direct(nthreads: int, iterations: int) -> list[Failure]:
    """Stress TimingListener directly via start_event/end_event."""
    listener = nb_event.TimingListener()
    nb_event.register(EVENT_KIND, listener)
    try:
        def worker(tid: int, iters: int,
                   failures: list[Failure], flock: threading.Lock) -> None:
            for i in range(iters):
                try:
                    nb_event.start_event(EVENT_KIND)
                    nb_event.end_event(EVENT_KIND)
                except Exception:
                    tb = traceback.format_exc()
                    with flock:
                        failures.append(Failure("direct", tid, i, tb))
                        if len(failures) > 32:
                            return

        failures = collect_failures(worker, nthreads, iterations, "direct")
    finally:
        # Best-effort cleanup; older numbas may not expose unregister.
        unregister = getattr(nb_event, "unregister", None)
        if callable(unregister):
            try:
                unregister(EVENT_KIND, listener)
            except Exception:
                pass

    print(f"[direct] listener._depth final = "
          f"{getattr(listener, '_depth', '<absent>')}")
    print(f"[direct] listener._ts present  = {hasattr(listener, '_ts')}")
    print(f"[direct] listener._duration    = "
          f"{getattr(listener, '_duration', '<absent>')}")
    return failures


# ---------------------------------------------------------------- compile ----

def make_unique_kernel(seed: int):
    """Build a distinct @jit kernel per call so the dispatcher cache cannot
    short-circuit compilation. Pure factory, no module-level state."""
    import numpy as np  # noqa: F401  (used inside the kernel body)
    const = float(seed) + 0.5

    @numba.jit
    def kernel(x):
        acc = 0.0
        for i in range(x.shape[0]):
            acc += x[i] ** 0.5 + const
        return acc

    return kernel


def run_compile(nthreads: int, iterations: int) -> list[Failure]:
    """Trigger many distinct compiles in parallel."""
    import numpy as np
    sample = np.linspace(0.0, 3.0, 32)

    def worker(tid: int, iters: int,
               failures: list[Failure], flock: threading.Lock) -> None:
        for i in range(iters):
            try:
                k = make_unique_kernel(tid * iters + i)
                k(sample)
            except Exception:
                tb = traceback.format_exc()
                with flock:
                    failures.append(Failure("compile", tid, i, tb))
                    if len(failures) > 32:
                        return

    return collect_failures(worker, nthreads, iterations, "compile")


# ------------------------------------------------------------------- main ----

def summarize(failures: list[Failure]) -> int:
    print("\n" + "=" * 72)
    if not failures:
        print("No failures observed. The race may still be latent.")
        print("Try a free-threaded interpreter (PYTHON_GIL=0 python3.14t),")
        print("more threads (-t 64), or more iterations (-n 20000).")
        return 0

    print(f"REPRODUCED: {len(failures)} failure(s).")
    seen: set[str] = set()
    samples_shown = 0
    for f in failures:
        sig_line = f.tb.splitlines()[-1] if f.tb else ""
        if sig_line in seen:
            continue
        seen.add(sig_line)
        samples_shown += 1
        print(f"\n--- sample failure ({samples_shown}) ---")
        print(f"mode={f.mode} thread={f.tid} iter={f.iteration}")
        print(f.tb)
    print(f"\nDistinct failure signatures: {len(seen)} "
          f"(out of {len(failures)} total)")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mode", choices=("direct", "compile", "both"),
                        default="direct")
    parser.add_argument("-t", "--threads", type=int, default=32)
    parser.add_argument("-n", "--iterations", type=int, default=2000)
    args = parser.parse_args()

    banner()

    failures: list[Failure] = []
    if args.mode in ("direct", "both"):
        failures.extend(run_direct(args.threads, args.iterations))
    if args.mode in ("compile", "both"):
        # Compiles are far slower than event broadcasts -- divide down.
        compile_iters = max(1, args.iterations // 50)
        failures.extend(run_compile(args.threads, compile_iters))

    return summarize(failures)


if __name__ == "__main__":
    sys.exit(main())
