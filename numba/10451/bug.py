import numpy as np
from numpy import zeros, int64
from numba import njit, typeof
import time
import numba as nb
from numba.experimental import jitclass

class timer_class():
    def __init__(self):
        self.tstart = time.time()

    def split(self):
        self.tend = time.time()
        self.tsplit = self.tend - self.tstart
        self.tstart = time.time()
        split = 0
        if (self.tsplit > 0):
            split = self.tsplit
        return split

arr_class_spec = [
    ("state_ix", nb.float64[:]),
    ("op_keys", typeof(int64(zeros( 64))) ),
]
@jitclass(arr_class_spec)
class arr_class_numba:
    def __init__(self, num_ops):
        state_ix = zeros(num_ops)
        self.state_ix = state_ix.astype(np.float64)
        op_keys = zeros(num_ops)
        self.op_keys = op_keys.astype(int64)

    def step(self):
        self.state_ix[0] = self.state_ix[self.op_keys[1]] + self.state_ix[self.op_keys[2]]

@njit
def iterate_method_test(
    arr_class, steps
):
    for step in range(steps):
        arr_class.step()


@njit
def iterate_fn_test(
    arr_class, steps
):
    for step in range(steps):
        arr_class.state_ix[0] = arr_class.state_ix[arr_class.op_keys[1]] + arr_class.state_ix[arr_class.op_keys[2]]

timer=timer_class()
arr_class=arr_class_numba(8) # cr
arr_class.state_ix[1]=100.0
arr_class.state_ix[2]=15.0
add_keys = np.asarray([1,2])
arr_class.op_keys[1:3] = add_keys.astype(int64)

# Now run the 2 variations:
# iterate_fn_test(): uses an external function to operate on the class object
# iterate_method_test():  uses a class method to operate on the class object
iterate_fn_test(arr_class, 1) # compile it
iterate_method_test(arr_class, 1) # compile it
n=100000000
t=timer.split();iterate_fn_test(arr_class, n);t=timer.split()
print(n,"iterations took", t,"seconds","with function numba", nb.__version__)
t=timer.split();iterate_method_test(arr_class, n);t=timer.split()
print(n,"iterations took", t,"seconds","with method numba", nb.__version__)
n=n*2
t=timer.split();iterate_fn_test(arr_class, n);t=timer.split()
print(n,"iterations took", t,"seconds","with function numba", nb.__version__)
t=timer.split();iterate_method_test(arr_class, n);t=timer.split()
print(n,"iterations took", t,"seconds","with method numba", nb.__version__)
print("Final value of operation:", arr_class.state_ix[0])
