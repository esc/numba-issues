import numba

@numba.njit
def foo(x, y, z=1):
    return x + y + z

assert foo(1, 1) == 3

@numba.njit
def bar(*xy, z=1):
    x, y = xy
    return x + y + z

assert bar(1, 1) == 3  # Raises TypingError: failed to unpack int64
