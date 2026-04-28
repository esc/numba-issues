"""Reproducer for numba/numba#10564 — TimingListener thread-safety.

Usage: PYTHON_GIL=0 python3.14t repro_no_pytest.py

Each thread does N paired on_start/on_end calls, so _depth must be 0
at the end. Any other value proves non-atomic corruption of the counter.
"""

import threading
from timeit import default_timer as timer
from numba.core.event import Event, EventStatus, TimingListener, Listener

KIND = "numba:compiler_lock"
THREADS = 16
ROUNDS = 50000

## Run With Numba impl. of TimingListener.

listener = TimingListener()
start_evt = Event(KIND, EventStatus.START)
end_evt = Event(KIND, EventStatus.END)
barrier = threading.Barrier(THREADS)

def worker():
    barrier.wait()
    for _ in range(ROUNDS):
        listener.on_start(start_evt)
        listener.on_end(end_evt)

threads = [threading.Thread(target=worker) for _ in range(THREADS)]
for t in threads:
    t.start()
for t in threads:
    t.join()

depth = listener._depth
if depth != 0:
    print(f"BUG: _depth={depth} (expected 0) — lost updates prove the race")
else:
    print(f"_depth=0 — race not observed (try native x86, not QEMU)")


## Run With fixed TimingListener, that has locks.

class MyTimingListener(Listener):

    def __init__(self):
        self._depth = 0
        self._lock = threading.Lock()

    def on_start(self, event):
        with self._lock:
            if self._depth == 0:
                self._ts = timer()
            self._depth += 1

    def on_end(self, event):
        with self._lock:
            self._depth -= 1
            if self._depth == 0:
                last = getattr(self, "_duration", 0)
                self._duration = (timer() - self._ts) + last

    @property
    def duration(self):
        with self._lock:
            return getattr(self, "_duration", None)

    @property
    def done(self):
        with self._lock:
            return hasattr(self, "_duration")


listener = MyTimingListener()
start_evt = Event(KIND, EventStatus.START)
end_evt = Event(KIND, EventStatus.END)
barrier = threading.Barrier(THREADS)

def worker():
    barrier.wait()
    for _ in range(ROUNDS):
        listener.on_start(start_evt)
        listener.on_end(end_evt)

threads = [threading.Thread(target=worker) for _ in range(THREADS)]
for t in threads:
    t.start()
for t in threads:
    t.join()

depth = listener._depth
if depth != 0:
    print(f"BUG: _depth={depth} (expected 0) — lost updates prove the race")
else:
    print(f"_depth=0 — race not observed (try native x86, not QEMU)")
