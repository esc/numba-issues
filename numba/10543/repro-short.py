"""Reproducer for numba/numba#10543 — ValueError vs TypingError."""
import numpy as np
from numba import jit
from numba.cpython.builtins import max_vararg

@jit(nopython=True)
def f(a, b):
    return max_vararg((a, b))

try:
    f(np.bool_(True), np.datetime64('2020', 'Y'))
except Exception as e:
    print(f"{type(e).__module__}.{type(e).__name__}: {str(e).splitlines()[0]}")
