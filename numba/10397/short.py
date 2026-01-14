import numpy as np
from numba import njit

@njit(fastmath=True)
def f(A):
    return np.linalg.slogdet(A)[1]

n = 100

A = np.random.rand(n, n) + 1j * np.random.rand(n, n)

print(f(A))
print(f(A))
