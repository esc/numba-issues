import numpy as np
import numba

@numba.njit
def add_0d(x, y):
    return x + y

@numba.njit
def problem(x, y):
    for i in range(10):
        x, y = x + y, x
    return x

a = np.zeros(())
b = np.ones(())
# It returns a float
print(type(add_0d(a, b)))  # <class 'float'>
problem(a, b)  # TypingError: Cannot unify array(float64, 0d, C) and float64 for 'x.2'
