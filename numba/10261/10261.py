from numba import jit 
from numpy import empty, random, uint64
from numpy.typing import NDArray
from enum import IntEnum

rng = random.default_rng(1337)  # Seed for reproducibility

class OP(IntEnum):
  NOT = 1

@jit(nopython=True) 
def fun(
  arr: NDArray,
) -> None:

  for addr in range(arr.shape[0]):
    val: uint64 = 0

    op = 1

    # Since op = 1, we should always go into the branch, and we do
    if op == OP.NOT:
      val = ~arr[addr]["word"]
      print("BEFORE", uint64(val))

    # The value here should be equal to the value reported in the "BEFORE" print
    # But it does not, it's something else
    print("AFTER ", uint64(val))

size = 1024
arr: NDArray = empty( size, dtype=[("word", uint64),],)
arr["word"] = rng.integers(low=0, high=2**64, size=size, dtype=uint64)

fun(arr)
