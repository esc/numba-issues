
import os, time
import numba
from numba.core import controlflow, bytecode

def make_chained_loops(n_loops):
    lines = ["def _f(x):"]
    for i in range(n_loops):
        lines.append(f"    i{i} = 0")
    for i in range(n_loops):
        lines.append(f"    while i{i} < 1:")
        lines.append(f"        i{i} += x")
    lines.append("    return x")
    src = "\n".join(lines)
    ns = {}
    exec(compile(src, "<generated>", "exec"), ns)
    return ns["_f"]

def bench_cfg(f, n=5):
    func_id = bytecode.FunctionIdentity.from_function(f)
    bc = bytecode.ByteCode(func_id)
    t0 = time.perf_counter()
    for _ in range(n):
        cfa = controlflow.ControlFlowAnalysis(bc)
        cfa.run()
    return (time.perf_counter() - t0) / n * 1e3

def bench_compile(f):
    jitted = numba.jit(f)
    t0 = time.perf_counter()
    jitted(1)
    return (time.perf_counter() - t0) * 1e3

CASES = [10, 50, 100, 150, 200, 250]
FULL_COMPILE = os.environ.get("BENCH_FULL_COMPILE")

if FULL_COMPILE:
    print(f"{'Loops':>8}  {'CFG (ms)':>10}  {'Compile (ms)':>14}")
    print("-" * 38)
else:
    print(f"{'Loops':>8}  {'CFG (ms)':>10}")
    print("-" * 22)

for n in CASES:
    f = make_chained_loops(n)
    cfg_ms = bench_cfg(f)
    if FULL_COMPILE:
        compile_ms = bench_compile(make_chained_loops(n))
        print(f"{n:>8}  {cfg_ms:>10.3f}  {compile_ms:>14.1f}")
    else:
        print(f"{n:>8}  {cfg_ms:>10.3f}")
