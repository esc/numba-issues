"""Reproducer for numba/numba#10543 — empty-tuple error message."""
from numba import jit

@jit(nopython=True)
def f():
    return max(())

try:
    f()
except Exception as e:
    msg = str(e)
    print(f"CLASS: {type(e).__module__}.{type(e).__name__}")
    print(f"HAS_EMPTY_TUPLE_MSG: {'empty tuple' in msg}")
    print(f"HAS_NO_MATCH_MSG:    {'No match' in msg or 'No implementation' in msg}")
    print("--- full message ---")
    print(msg)
