from numba import njit
import numpy as np


def generate_code(count):
    base_code = """
    dependency_{index} = 1 if True else 0
    value_{index} = x if dependency_{index} else 0"""

    code = """
@njit
def template(x):"""
    for i in range(count):
        code += base_code.format(**{'index': i})
    return code

if __name__ == '__main__':
    import sys
    import time


    count = int(sys.argv[1])

    exec(generate_code(count), globals(), locals())
    start = time.time()
    template(32)
    end = time.time()
    print(end - start, 'elapsed')
