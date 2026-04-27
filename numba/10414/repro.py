from numba import njit

@njit()
def jitted(low):
    val = None

    for _ in range(low, 2):
        val = 'garbage'

    if val == None:
        print('jit: loop had no iterations')
    else:
        print('jit: loop had an iteration')

def interpreted(low):
    val = None

    for _ in range(low, 2):
        val = 'garbage'

    if val == None:
        print('interpreter: loop had no iterations')
    else:
        print('interpreter: loop had an iteration')

jitted(5)
interpreted(5)
