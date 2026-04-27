"""
Reproducer for numba/numba#10543 — ValueError vs TypingError on the
unification-failure path (v2).

Strategy:
  1. Enumerate Number, NPDatetime, NPTimedelta types and find any pair
     that unify_types() rejects.
  2. Exercise the failure via:
     (a) the overload path (min/max on the numeric pair, if found), and
     (b) a direct call into the @intrinsic max_vararg, which bypasses the
         overload's isinstance(ty, Number) filter.

Expected:
  main       -> TypingError (no matching signature)
  PR f0fc69d -> ValueError  ("Given types cannot be unified")
"""
import itertools
import numpy as np

from numba import jit, types
from numba.core.errors import TypingError
from numba.core.registry import cpu_target
from numba.np.types import NPDatetime, NPTimedelta


def _all_candidate_types():
    numbers = [
        types.boolean,
        types.int8, types.int16, types.int32, types.int64,
        types.uint8, types.uint16, types.uint32, types.uint64,
        types.float32, types.float64,
        types.complex64, types.complex128,
    ]
    units = ['Y', 'M', 'W', 'D', 'h', 'm', 's', 'ms', 'us', 'ns']
    dts = [NPDatetime(u) for u in units]
    tds = [NPTimedelta(u) for u in units]
    return numbers, dts, tds


def find_nonunifiable_pairs():
    ctx = cpu_target.typing_context
    ctx.refresh()
    numbers, dts, tds = _all_candidate_types()
    all_types = numbers + dts + tds

    for a, b in itertools.product(all_types, repeat=2):
        if a == b:
            continue
        try:
            if ctx.unify_types(a, b) is None:
                yield a, b
        except Exception:
            # Some pairs raise rather than return None; treat that as
            # "won't unify" too.
            yield a, b


def classify(exc):
    qualname = f"{type(exc).__module__}.{type(exc).__name__}"
    tag = "TypingError" if isinstance(exc, TypingError) else "OTHER"
    return tag, qualname


def run(label, fn, *args):
    try:
        result = fn(*args)
        print(f"  {label:<55} ok -> {result!r}")
    except Exception as e:
        tag, qualname = classify(e)
        head = (str(e).strip().splitlines() or ["<empty>"])[0]
        print(f"  {label:<55} [{tag}] {qualname}")
        print(f"  {'':<55}   {head[:120]}")


# ---- overload-path jitted wrappers -----------------------------------------

@jit(nopython=True)
def _min2(a, b):
    return min(a, b)


@jit(nopython=True)
def _max2(a, b):
    return max(a, b)


# ---- direct-intrinsic path -------------------------------------------------
# Import the intrinsic itself and call it from jitted code. This bypasses the
# overload's isinstance(ty, Number) filter entirely, so ANY non-unifiable
# pair lands in the unify_types(...) is None branch.

from numba.cpython.builtins import max_vararg, min_vararg  # noqa: E402


@jit(nopython=True)
def _max_vararg_direct(a, b):
    return max_vararg((a, b))


@jit(nopython=True)
def _min_vararg_direct(a, b):
    return min_vararg((a, b))


# ---- concrete value helpers ------------------------------------------------

_NP_NUMBER = {
    types.boolean:    lambda: np.bool_(True),
    types.int8:       lambda: np.int8(-1),
    types.int16:      lambda: np.int16(-1),
    types.int32:      lambda: np.int32(-1),
    types.int64:      lambda: np.int64(-1),
    types.uint8:      lambda: np.uint8(1),
    types.uint16:     lambda: np.uint16(1),
    types.uint32:     lambda: np.uint32(1),
    types.uint64:     lambda: np.uint64(1),
    types.float32:    lambda: np.float32(1.0),
    types.float64:    lambda: np.float64(1.0),
    types.complex64:  lambda: np.complex64(1+0j),
    types.complex128: lambda: np.complex128(1+0j),
}


def make_value(t):
    if t in _NP_NUMBER:
        return _NP_NUMBER[t]()
    if isinstance(t, NPDatetime):
        return np.datetime64('2020-01-01', t.unit)
    if isinstance(t, NPTimedelta):
        return np.timedelta64(1, t.unit)
    return None


def main():
    pairs = list(find_nonunifiable_pairs())
    print(f"Found {len(pairs)} non-unifiable ordered pairs.\n")

    if not pairs:
        print("unify_types accepts everything we tried — nothing to demo.")
        return

    # Pick up to 3 representative pairs: one pure-Number if any,
    # one involving datetimes if any, one involving timedeltas if any.
    picks = []

    def pick_where(pred):
        for p in pairs:
            if pred(p) and p not in picks:
                picks.append(p)
                return

    pick_where(lambda p: all(isinstance(t, types.Number) for t in p))
    pick_where(lambda p: any(isinstance(t, NPDatetime) for t in p))
    pick_where(lambda p: any(isinstance(t, NPTimedelta) for t in p))

    if not picks:
        picks = pairs[:3]

    for ta, tb in picks:
        print(f"--- pair: {ta}  +  {tb} ---")
        a, b = make_value(ta), make_value(tb)
        if a is None or b is None:
            print("  (no concrete value available)\n")
            continue

        # Overload path: only meaningful when both are Number (or both
        # datetime-family — handled by the datetime_registry overload).
        both_number = all(isinstance(t, types.Number) for t in (ta, tb))
        both_dt_fam = all(isinstance(t, (NPDatetime, NPTimedelta))
                          for t in (ta, tb))
        if both_number or both_dt_fam:
            run(f"min({ta}, {tb}) via overload", _min2, a, b)
            run(f"max({ta}, {tb}) via overload", _max2, a, b)

        # Direct intrinsic path: always runs.
        run(f"max_vararg(({ta}, {tb})) direct", _max_vararg_direct, a, b)
        run(f"min_vararg(({ta}, {tb})) direct", _min_vararg_direct, a, b)
        print()


if __name__ == "__main__":
    main()
