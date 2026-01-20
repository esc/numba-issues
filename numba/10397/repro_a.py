import timeit
import numpy as np
from numba import njit
from functools import partial

@njit(fastmath=True)
def f(A):
    return np.linalg.slogdet(A)[1]


n = 3 * 513
A = np.random.rand(n, n) + 1j * np.random.rand(n, n)
print(np.allclose(f.py_func(A), f(A)))
print(min(timeit.Timer(partial(f.py_func, A)).repeat(2, 10)) / 10)
print(min(timeit.Timer(partial(f, A)).repeat(2, 10)) / 10)
