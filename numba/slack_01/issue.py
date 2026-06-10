import time
import numba as nb
import numpy as np

N = 1_000_000

@nb.jit
def collatz_length(n):
    length = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        length += 1
    return length

@nb.jit(parallel=True)
def compute_parallel_slow(limit):
    out = np.zeros(limit)
    for i in nb.prange(limit):
        out[i] = collatz_length(i)
    return out

@nb.jit(parallel=True)
def compute_parallel_fast(limit):
    out = np.zeros(limit)
    for i in nb.prange(0.0, limit):
        out[i] = collatz_length(i)
    return out

compute_parallel_slow(N)
compute_parallel_fast(N)

t0 = time.perf_counter(); compute_parallel_slow(N); print(f"slow: {time.perf_counter()-t0:.3f}s")
t0 = time.perf_counter(); compute_parallel_fast(N); print(f"fast: {time.perf_counter()-t0:.3f}s")
