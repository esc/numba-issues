from numba import njit

@njit
def f():
    x = None
    return x == None

assert f.py_func() == f(), f"py={f.py_func()}, jit={f()}"
