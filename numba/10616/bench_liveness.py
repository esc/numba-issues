"""Benchmark for numba PR #10616.

Demonstrates that iterating the liveness fix-point in *topological* order
(instead of dict-insertion order) cuts the number of fix-point passes from
O(loop-depth / chain-length) to a small constant.

Self-contained: does NOT import numba. It reproduces the exact fix-point
logic of ``numba.core.analysis.compute_live_map`` and
``compute_live_variables`` and only varies the iteration order, so the two
variants are guaranteed to compute the same result (asserted below) -- the
change is behavior-preserving.

Fixed seed, best-of-5. Absolute milliseconds depend on the machine; the
point is the asymptotic trend (iteration count) and the speedup.
"""

import random
from time import perf_counter


# --------------------------------------------------------------------------
# Synthetic CFG: a chain 0 -> 1 -> ... -> (n-1) plus back-edges every `step`
# blocks (each back-edge makes a loop), so the graph is loop-heavy and
# reducible -- like a real Numba CFG with nested/sequential loops.
#
# A variable "x" is defined at the entry block and used at the exit block, so
# liveness must propagate the full length of the chain. That long-distance
# backward propagation is what the old dict-order pass did one block at a time.
# --------------------------------------------------------------------------
def make_cfg(n_nodes, seed, step=10):
    rng = random.Random(seed)
    succs = {i: [] for i in range(n_nodes)}
    preds = {i: [] for i in range(n_nodes)}

    def add_edge(a, b):
        succs[a].append(b)
        preds[b].append(a)

    for i in range(n_nodes - 1):
        add_edge(i, i + 1)
    # back-edges -> loops
    for header in range(step, n_nodes - 1, step):
        latch = min(header + rng.randint(1, step - 1), n_nodes - 1)
        add_edge(latch, header)

    # one variable defined at entry, used at exit -> forces full propagation
    var_use_map = {i: set() for i in range(n_nodes)}
    var_def_map = {i: set() for i in range(n_nodes)}
    var_def_map[0] = {"x"}
    var_use_map[n_nodes - 1] = {"x"}
    # sprinkle a few locals so the sets are non-trivial
    for i in range(0, n_nodes, step):
        var_def_map[i] |= {f"t{i}"}
        if i + 1 < n_nodes:
            var_use_map[i + 1] |= {f"t{i}"}

    return succs, preds, var_use_map, var_def_map


def topo_order(n_nodes, succs):
    """Reverse-postorder DFS ignoring back-edges == a valid topological
    order of a reducible CFG (this is what cfg.topo_order() returns)."""
    seen = set()
    post = []
    for root in range(n_nodes):
        if root in seen:
            continue
        stack = [(root, iter(succs[root]))]
        seen.add(root)
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append((nxt, iter(succs[nxt])))
                    advanced = True
                    break
            if not advanced:
                post.append(node)
                stack.pop()
    post.reverse()
    return post


# --------------------------------------------------------------------------
# The fix-point itself -- identical logic to numba.core.analysis. The ONLY
# thing the PR changes is `forward_order` / `backward_order`.
# --------------------------------------------------------------------------
def compute_live_map(blocks, succs, preds, var_use_map, var_def_map,
                     forward_order, backward_order):
    n_iters = [0]

    def fix_point_progress(dct):
        return tuple(len(v) for v in dct.values())

    def fix_point(fn, dct):
        old_point = None
        new_point = fix_point_progress(dct)
        while old_point != new_point:
            fn(dct)
            n_iters[0] += 1
            old_point = new_point
            new_point = fix_point_progress(dct)

    def def_reach(dct):
        for offset in forward_order:
            if offset not in var_def_map:
                continue
            used_or_defined = var_def_map[offset] | var_use_map[offset]
            dct[offset] |= used_or_defined
            for out_blk in succs[offset]:
                dct[out_blk] |= dct[offset]

    def liveness(dct):
        for offset in backward_order:
            if offset not in dct:
                continue
            live_vars = dct[offset]
            for inc_blk in preds[offset]:
                reachable = live_vars & def_reach_map[inc_blk]
                dct[inc_blk] |= reachable - var_def_map[inc_blk]

    live_map = {off: set(var_use_map[off]) for off in blocks}
    def_reach_map = {off: set() for off in blocks}
    fix_point(def_reach, def_reach_map)
    fix_point(liveness, live_map)
    return live_map, n_iters[0]


def best_of(fn, repeats=5):
    best = float("inf")
    result = None
    for _ in range(repeats):
        t0 = perf_counter()
        result = fn()
        best = min(best, perf_counter() - t0)
    return best, result


GRID = [30, 100, 300, 500, 1000]

print("compute_live_map  (PR #10616, commit 1)")
print(f"{'Blocks':>8} {'Old (ms)':>10} {'Old iters':>10} "
      f"{'New (ms)':>10} {'New iters':>10} {'Speedup':>9}")
for n in GRID:
    succs, preds, use_map, def_map = make_cfg(n, seed=n)
    blocks = {i: None for i in range(n)}
    ins = list(range(n))                      # dict-insertion order
    topo = topo_order(n, succs)               # cfg.topo_order()
    rtopo = list(reversed(topo))

    old_t, (old_lm, old_it) = best_of(
        lambda: compute_live_map(blocks, succs, preds, use_map, def_map,
                                 ins, ins))            # old: dict order both
    new_t, (new_lm, new_it) = best_of(
        lambda: compute_live_map(blocks, succs, preds, use_map, def_map,
                                 topo, rtopo))         # new: topo / reverse
    assert old_lm == new_lm, "results diverge -> not behavior-preserving!"
    print(f"{n:>8} {old_t * 1e3:>10.2f} {old_it:>10} "
          f"{new_t * 1e3:>10.2f} {new_it:>10} {old_t / new_t:>8.1f}x")


# --------------------------------------------------------------------------
# compute_live_variables (PR #10616, commit 2). Forward-only fix-point.
# This is a *defensive* fix: when blocks happen to be stored in topological
# order (the common case) it is ~1x. But after inlining/merging passes
# renumber and re-order blocks, dict-insertion order can be far from topo
# order -- then the old `for offset in blocks` loop pays O(reorder-distance)
# extra passes. We show both: natural order (~1x) and a shuffled-order CFG
# (the pathological case the fix protects against), at zero cost.
# --------------------------------------------------------------------------
def compute_live_variables(blocks_order, succs, var_def_map, var_dead_map,
                           iter_order):
    n_iters = [0]
    block_entry_vars = {off: set() for off in blocks_order}

    def fix_point_progress():
        return tuple(len(v) for v in block_entry_vars.values())

    old_point = None
    new_point = fix_point_progress()
    while old_point != new_point:
        for offset in iter_order:
            avail = block_entry_vars[offset] | var_def_map[offset]
            avail -= var_dead_map[offset]
            for succ in succs[offset]:
                block_entry_vars[succ] |= avail
        n_iters[0] += 1
        old_point = new_point
        new_point = fix_point_progress()
    return block_entry_vars, n_iters[0]


print()
print("compute_live_variables  (PR #10616, commit 2)")
print(f"{'Blocks':>8} {'Order':>12} {'Old iters':>10} {'New iters':>10} "
      f"{'Speedup':>9}")
for n in GRID:
    succs, preds, use_map, def_map = make_cfg(n, seed=n)
    var_dead_map = {i: set() for i in range(n)}   # nothing dies -> max prop.
    topo = topo_order(n, succs)

    for label, insertion in (("natural", list(range(n))),
                             ("shuffled", None)):
        if insertion is None:
            insertion = list(range(n))
            random.Random(n).shuffle(insertion)   # simulate renumbering
        old_t, (old_r, old_it) = best_of(
            lambda: compute_live_variables(insertion, succs, def_map,
                                           var_dead_map, insertion))
        new_t, (new_r, new_it) = best_of(
            lambda: compute_live_variables(insertion, succs, def_map,
                                           var_dead_map, topo))
        assert old_r == new_r, "results diverge -> not behavior-preserving!"
        print(f"{n:>8} {label:>12} {old_it:>10} {new_it:>10} "
              f"{old_t / new_t:>8.1f}x")
