import timeit
import numpy as np
from numba import njit
from functools import partial

@njit(fastmath=True)
def f(A, b):
    return np.linalg.solve(A, b)


n = 3 * 513
A = np.random.rand(n, n) + 1j * np.random.rand(n, n)
b = np.random.rand(n) + 1j * np.random.rand(n)
print(np.allclose(f.py_func(A, b), f(A, b)))
print(min(timeit.Timer(partial(f.py_func, A, b)).repeat(2, 10)) / 10)
print(min(timeit.Timer(partial(f, A, b)).repeat(2, 10)) / 10)
