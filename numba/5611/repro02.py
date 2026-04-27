from numba import njit
import numpy as np


def generate_code(count):
    base_code = """
    dependency_{index} = 1 if True else 0
    value_{index} = x if dependendency_{index} else 0"""

    code = """
@njit
def template(x):"""
    for i in range(count):
        code += base_code.format(**{'index': i})
    return code

def show_cfg(fn):
    from numba.core.controlflow import ControlFlowAnalysis
    from numba.core.bytecode import FunctionIdentity, ByteCode
    fid = FunctionIdentity.from_function(fn)
    bc = ByteCode(func_id=fid)
    cfa = ControlFlowAnalysis(bc)
    cfa.run()
    cfa.graph.render_dot().view()

if __name__ == '__main__':
    import sys
    import time

    count = int(sys.argv[1])
    genned = generate_code(count)
    print(genned)
    exec(genned, globals(), locals())
    start = time.time()
    template(32)
    show_cfg(template)
    end = time.time()
    print(end - start, 'elapsed')
