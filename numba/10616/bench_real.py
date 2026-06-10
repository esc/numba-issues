"""Measures the REAL numba.core.analysis functions (not a reimplementation).

Builds real CFGraph CFGs and calls the actual compute_live_map /
compute_live_variables. Run once on this branch and once with analysis.py
checked out to main; the iteration-order change lives entirely in that file
(pure Python), so no rebuild is needed to switch versions.
"""
import random
from time import perf_counter

from numba.core.analysis import compute_live_map, compute_live_variables
from numba.core.controlflow import CFGraph


def make_cfg(n, seed, step=10):
    g = CFGraph()
    for i in range(n):
        g.add_node(i)
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    rng = random.Random(seed)
    for header in range(step, n - 1, step):
        latch = min(header + rng.randint(1, step - 1), n - 1)
        g.add_edge(latch, header)
    g.set_entry_point(0)
    g.process()

    blocks = {i: None for i in range(n)}          # only keys are used
    use = {i: set() for i in range(n)}
    dfn = {i: set() for i in range(n)}
    dead = {i: set() for i in range(n)}
    dfn[0] = {"x"}
    use[n - 1] = {"x"}                             # def@entry, use@exit
    for i in range(0, n, step):
        dfn[i] |= {f"t{i}"}
        if i + 1 < n:
            use[i + 1] |= {f"t{i}"}
    return g, blocks, use, dfn, dead


def best_of(fn, repeats=5):
    best = float("inf")
    for _ in range(repeats):
        t0 = perf_counter()
        fn()
        best = min(best, perf_counter() - t0)
    return best


GRID = [30, 100, 300, 500, 1000]
print(f"{'Blocks':>8} {'live_map(ms)':>13} {'live_vars(ms)':>14}")
for n in GRID:
    g, blocks, use, dfn, dead = make_cfg(n, seed=n)
    t_lm = best_of(lambda: compute_live_map(g, blocks, use, dfn))
    t_lv = best_of(lambda: compute_live_variables(g, blocks, dfn, dead))
    print(f"{n:>8} {t_lm * 1e3:>13.3f} {t_lv * 1e3:>14.3f}")
