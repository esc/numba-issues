import random
from time import perf_counter


def find_back_edges_list(succs, entry_point):
    """Original: `cur_node in stack` -> O(stack depth) per edge -> O(V*E)."""
    back_edges = set()
    stack = []
    succs_state = {}
    checked = set()

    def push_state(node):
        stack.append(node)
        succs_state[node] = [dest for dest in succs[node]]

    push_state(entry_point)
    while stack:
        tos = stack[-1]
        tos_succs = succs_state[tos]
        if tos_succs:
            cur_node = tos_succs.pop()
            if cur_node in stack:           # O(n) linear scan of the list
                back_edges.add((tos, cur_node))
            elif cur_node not in checked:
                push_state(cur_node)
        else:
            stack.pop()
            checked.add(tos)
    return back_edges


def find_back_edges_set(succs, entry_point):
    """New: parallel `on_stack` set -> O(1) per edge -> O(V+E)."""
    back_edges = set()
    stack = []
    on_stack = set()
    succs_state = {}
    checked = set()

    def push_state(node):
        stack.append(node)
        on_stack.add(node)
        succs_state[node] = [dest for dest in succs[node]]

    push_state(entry_point)
    while stack:
        tos = stack[-1]
        tos_succs = succs_state[tos]
        if tos_succs:
            cur_node = tos_succs.pop()
            if cur_node in on_stack:        # O(1) set membership
                back_edges.add((tos, cur_node))
            elif cur_node not in checked:
                push_state(cur_node)
        else:
            stack.pop()
            on_stack.remove(tos)
            checked.add(tos)
    return back_edges


def make_cfg(n_nodes, n_back, seed):
    """Chain 0->1->...->(n-1) plus `n_back` random back-edges s->t with t < s."""
    rng = random.Random(seed)
    succs = {i: [] for i in range(n_nodes)}
    for i in range(n_nodes - 1):
        succs[i].append(i + 1)
    for _ in range(n_back):
        s = rng.randint(1, n_nodes - 1)
        t = rng.randint(0, s - 1)
        succs[s].append(t)
    return succs


def best_of(fn, succs, entry, repeats=5):
    best = float("inf")
    for _ in range(repeats):
        t0 = perf_counter()
        result = fn(succs, entry)
        best = min(best, perf_counter() - t0)
    return best, result


GRID = [(100, 10), (500, 50), (1_000, 100), (5_000, 500),
        (10_000, 1_000), (50_000, 5_000)]

print(f"{'Nodes':>8} {'Back-edges':>11} {'Old (ms)':>10} "
      f"{'New (ms)':>10} {'Speedup':>9}")
for n_nodes, n_back in GRID:
    succs = make_cfg(n_nodes, n_back, seed=n_nodes)
    old_t, old_r = best_of(find_back_edges_list, succs, 0)
    new_t, new_r = best_of(find_back_edges_set, succs, 0)
    assert old_r == new_r, "results diverge -> not behavior-preserving!"
    print(f"{n_nodes:>8} {n_back:>11} {old_t * 1e3:>10.2f} "
          f"{new_t * 1e3:>10.2f} {old_t / new_t:>8.1f}x")
