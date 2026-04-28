import threading

import pytest
from numba.core import event as ev
from numba.core.event import Event, EventStatus, TimingListener
from numba.core.compiler_lock import global_compiler_lock


@pytest.mark.parallel_threads_limit(8)
def test_numba_compiler_timing_race():
    for _ in range(20_000):
        with ev.install_timer("numba:compiler_lock", lambda dur: None):
            with global_compiler_lock:
                pass


shared_listener = TimingListener()
start = Event("numba:compiler_lock", EventStatus.START)
end = Event("numba:compiler_lock", EventStatus.END)
barriers = {}
barriers_lock = threading.Lock()


def get_barrier(n):
    with barriers_lock:
        barrier = barriers.get(n)
        if barrier is None:
            barrier = threading.Barrier(n)
            barriers[n] = barrier
        return barrier


@pytest.mark.parallel_threads_limit(8)
def test_timing_listener_not_thread_safe_in_general(thread_index, num_parallel_threads):
    for _ in range(200_000):
        shared_listener.notify(start)
        shared_listener.notify(end)

    get_barrier(num_parallel_threads).wait()
    if thread_index == 0:
        assert shared_listener._depth == 0
