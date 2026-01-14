import numpy as np
from numba import njit

@njit
def f(z):
    return np.tanh(z)

print(np.tanh(1e2 + 1j), f.py_func(1e2 + 1j), f(1e2 + 1j))
print(np.tanh(1e8 + 1j), f.py_func(1e8 + 1j), f(1e8 + 1j))
