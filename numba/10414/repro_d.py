from numba import njit

@njit
def f():
    x = None
    for _ in range(0):
        x = 'v'
    return x == None

assert f.py_func() == f(), f"py={f.py_func()}, jit={f()}"
