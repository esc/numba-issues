from numba import njit

@njit
def g():
    print("one")
    x = None
    print("two")
    for _ in range(0):
        x = 'v'
    print("three")
    return x != None

assert g.py_func() == g()#, f"py={g.py_func()}, jit={g()}"
