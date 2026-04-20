bisect-harness
--------------

This is a harness for doing a `git bisect` on cpython.

usage
-----

This harness assumes you have `docker` installed and runnable.

This harness assumes the following repositpories have been cloned:

```
https://github.com/esc/numba-issues --> ~/git/numba-issues/
https://github.com/python/cpython --> ~/git/cpython
```

The you have to build the dockerfile:

```
cd  ~/git/numba-issues/numba/10538/bisect-harness
docker build --no-cache -t cpython-bisect-base -f Dockerfile.base .
```

And then you can run the `git bisect` using:

```
cd ~/git/cpython
git bisect start && git bisect bad v3.14.4 && git bisect good v3.14.3
git bisect run ~/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh
```

results
-------

```
esc@artemis [base] [cpython:v3.14.4~31:★★:bisect] ~/git/cpython git bisect reset && git bisect start && git bisect bad v3.14.4 && git bisect good v3.14.3

Previous HEAD position was 25b48b84b8 [3.14] gh-143050: Correct PyLong_FromString() to use _PyLong_Negate() (GH-145901) (#147331)
Switched to branch 'VAL'
status: waiting for both good and bad commits
status: waiting for good commit(s), bad commit known
Bisecting: 168 revisions left to test after this (roughly 7 steps)
[e12cc266161440e4528213e2b18a15de8afec408] [3.14] gh-145010: Fix Python.h compilation with -masm=intel (GH-145011) (#145776)
esc@artemis [base] [cpython:v3.14.4~169:★★:bisect] ~/git/cpython git bisect run ~/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at e12cc266161
==> Installing Numba deps
==> Running tests
Bisecting: 84 revisions left to test after this (roughly 6 steps)
[abd276ab3dc452d1ecc2e1cd34df84d2cd26348d] [3.14] docs: fix f-string in ExceptionGroup example (GH-146108) (GH-146126)
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at abd276ab3dc
==> Installing Numba deps
==> Running tests
Bisecting: 42 revisions left to test after this (roughly 5 steps)
[836e5abfb3616c025c82bf99f5bd7c7b7ab97627] [3.14] gh-146444: Make Platforms/Apple/ compatible with Python 3.9 (GH-146624) (#146627)
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at 836e5abfb36
==> Installing Numba deps
==> Running tests
Bisecting: 21 revisions left to test after this (roughly 5 steps)
[f4c9bc899b982b9742b45cff0643fa34de3dc84d] [3.14] gh-126676: Expand argparse docs for type=bool with warning and alternatives (GH-146435) (#148048)
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at f4c9bc899b9
==> Installing Numba deps
==> Running tests
ERROR: test_raising_callback_unwinds_from_jit_on_unwind_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_unwind_path)
Traceback (most recent call last):
FAIL: test_profiler (numba.tests.test_profiler.TestProfiler.test_profiler)
Traceback (most recent call last):
FAIL: test_profiler_for_raising_function (numba.tests.test_profiler.TestProfiler.test_profiler_for_raising_function)
Traceback (most recent call last):
FAIL: test_call_event_chain (numba.tests.test_sys_monitoring.TestMonitoring.test_call_event_chain)
Traceback (most recent call last):
FAIL: test_monitoring_multiple_threads (numba.tests.test_sys_monitoring.TestMonitoring.test_monitoring_multiple_threads)
Traceback (most recent call last):
FAIL: test_multiple_tool_id (numba.tests.test_sys_monitoring.TestMonitoring.test_multiple_tool_id)
Traceback (most recent call last):
FAIL: test_mutation_from_objmode (numba.tests.test_sys_monitoring.TestMonitoring.test_mutation_from_objmode)
Traceback (most recent call last):
FAIL: test_raising_callback_unwinds_from_jit_on_raising_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_raising_path)
Traceback (most recent call last):
FAIL: test_raising_callback_unwinds_from_jit_on_success_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_success_path)
Traceback (most recent call last):
FAIL: test_raising_under_monitoring (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_under_monitoring)
Traceback (most recent call last):
FAIL: test_return_event (numba.tests.test_sys_monitoring.TestMonitoring.test_return_event)
Traceback (most recent call last):
FAIL: test_start_event (numba.tests.test_sys_monitoring.TestMonitoring.test_start_event)
Traceback (most recent call last):
FAIL: test_stop_iteration_under_monitoring (numba.tests.test_sys_monitoring.TestMonitoring.test_stop_iteration_under_monitoring)
Traceback (most recent call last):
FAILED (failures=12, errors=1, skipped=1)
Traceback (most recent call last):
Bisecting: 10 revisions left to test after this (roughly 3 steps)
[2d1515dc21c7dea433fe639c6c8ca249986a6a7e] [3.14] gh-145563: Add thread-safety annotation for PyCapsule C-API (GH-146612) (#146659)
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at 2d1515dc21c
==> Installing Numba deps
==> Running tests
Bisecting: 5 revisions left to test after this (roughly 3 steps)
[ea9ecc8955a77365ffdf1c787f8eeb03a54df330] [3.14] gh-146488: hash-pin all action references (gh-146489) (#147983)
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at ea9ecc8955a
==> Installing Numba deps
==> Running tests
ERROR: test_raising_callback_unwinds_from_jit_on_unwind_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_unwind_path)
Traceback (most recent call last):
FAIL: test_profiler (numba.tests.test_profiler.TestProfiler.test_profiler)
Traceback (most recent call last):
FAIL: test_profiler_for_raising_function (numba.tests.test_profiler.TestProfiler.test_profiler_for_raising_function)
Traceback (most recent call last):
FAIL: test_call_event_chain (numba.tests.test_sys_monitoring.TestMonitoring.test_call_event_chain)
Traceback (most recent call last):
FAIL: test_monitoring_multiple_threads (numba.tests.test_sys_monitoring.TestMonitoring.test_monitoring_multiple_threads)
Traceback (most recent call last):
FAIL: test_multiple_tool_id (numba.tests.test_sys_monitoring.TestMonitoring.test_multiple_tool_id)
Traceback (most recent call last):
FAIL: test_mutation_from_objmode (numba.tests.test_sys_monitoring.TestMonitoring.test_mutation_from_objmode)
Traceback (most recent call last):
FAIL: test_raising_callback_unwinds_from_jit_on_raising_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_raising_path)
Traceback (most recent call last):
FAIL: test_raising_callback_unwinds_from_jit_on_success_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_success_path)
Traceback (most recent call last):
FAIL: test_raising_under_monitoring (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_under_monitoring)
Traceback (most recent call last):
FAIL: test_return_event (numba.tests.test_sys_monitoring.TestMonitoring.test_return_event)
Traceback (most recent call last):
FAIL: test_start_event (numba.tests.test_sys_monitoring.TestMonitoring.test_start_event)
Traceback (most recent call last):
FAIL: test_stop_iteration_under_monitoring (numba.tests.test_sys_monitoring.TestMonitoring.test_stop_iteration_under_monitoring)
Traceback (most recent call last):
FAILED (failures=12, errors=1, skipped=1)
Traceback (most recent call last):
Bisecting: 2 revisions left to test after this (roughly 1 step)
[25b48b84b85a08384479d2636a01d1d52fa97a6b] [3.14] gh-143050: Correct PyLong_FromString() to use _PyLong_Negate() (GH-145901) (#147331)
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at 25b48b84b85
==> Installing Numba deps
==> Running tests
Bisecting: 0 revisions left to test after this (roughly 1 step)
[b406d85603d5099e415da04e7b6559a51f145595] [3.14] gh-146615: Fix format specifiers in extension modules (GH-146617) (#147704)
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at b406d85603d
==> Installing Numba deps
==> Running tests
ERROR: test_raising_callback_unwinds_from_jit_on_unwind_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_unwind_path)
Traceback (most recent call last):
FAIL: test_profiler (numba.tests.test_profiler.TestProfiler.test_profiler)
Traceback (most recent call last):
FAIL: test_profiler_for_raising_function (numba.tests.test_profiler.TestProfiler.test_profiler_for_raising_function)
Traceback (most recent call last):
FAIL: test_call_event_chain (numba.tests.test_sys_monitoring.TestMonitoring.test_call_event_chain)
Traceback (most recent call last):
FAIL: test_monitoring_multiple_threads (numba.tests.test_sys_monitoring.TestMonitoring.test_monitoring_multiple_threads)
Traceback (most recent call last):
FAIL: test_multiple_tool_id (numba.tests.test_sys_monitoring.TestMonitoring.test_multiple_tool_id)
Traceback (most recent call last):
FAIL: test_mutation_from_objmode (numba.tests.test_sys_monitoring.TestMonitoring.test_mutation_from_objmode)
Traceback (most recent call last):
FAIL: test_raising_callback_unwinds_from_jit_on_raising_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_raising_path)
Traceback (most recent call last):
FAIL: test_raising_callback_unwinds_from_jit_on_success_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_success_path)
Traceback (most recent call last):
FAIL: test_raising_under_monitoring (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_under_monitoring)
Traceback (most recent call last):
FAIL: test_return_event (numba.tests.test_sys_monitoring.TestMonitoring.test_return_event)
Traceback (most recent call last):
FAIL: test_start_event (numba.tests.test_sys_monitoring.TestMonitoring.test_start_event)
Traceback (most recent call last):
FAIL: test_stop_iteration_under_monitoring (numba.tests.test_sys_monitoring.TestMonitoring.test_stop_iteration_under_monitoring)
Traceback (most recent call last):
FAILED (failures=12, errors=1, skipped=1)
Traceback (most recent call last):
Bisecting: 0 revisions left to test after this (roughly 0 steps)
[6ea4f842fb699a5cd34ec5bed98e259c47e02ca1] [3.14] gh-144438: Fix false sharing between QSBR and tlbc_index (gh-144554) (#144923)
running '/Users/esc/git/numba-issues/numba/10538/bisect-harness/bisect_run.sh'
==> Building CPython at 6ea4f842fb6
==> Installing Numba deps
==> Running tests
ERROR: test_raising_callback_unwinds_from_jit_on_unwind_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_unwind_path)
Traceback (most recent call last):
FAIL: test_profiler (numba.tests.test_profiler.TestProfiler.test_profiler)
Traceback (most recent call last):
FAIL: test_profiler_for_raising_function (numba.tests.test_profiler.TestProfiler.test_profiler_for_raising_function)
Traceback (most recent call last):
FAIL: test_call_event_chain (numba.tests.test_sys_monitoring.TestMonitoring.test_call_event_chain)
Traceback (most recent call last):
FAIL: test_monitoring_multiple_threads (numba.tests.test_sys_monitoring.TestMonitoring.test_monitoring_multiple_threads)
Traceback (most recent call last):
FAIL: test_multiple_tool_id (numba.tests.test_sys_monitoring.TestMonitoring.test_multiple_tool_id)
Traceback (most recent call last):
FAIL: test_mutation_from_objmode (numba.tests.test_sys_monitoring.TestMonitoring.test_mutation_from_objmode)
Traceback (most recent call last):
FAIL: test_raising_callback_unwinds_from_jit_on_raising_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_raising_path)
Traceback (most recent call last):
FAIL: test_raising_callback_unwinds_from_jit_on_success_path (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_callback_unwinds_from_jit_on_success_path)
Traceback (most recent call last):
FAIL: test_raising_under_monitoring (numba.tests.test_sys_monitoring.TestMonitoring.test_raising_under_monitoring)
Traceback (most recent call last):
FAIL: test_return_event (numba.tests.test_sys_monitoring.TestMonitoring.test_return_event)
Traceback (most recent call last):
FAIL: test_start_event (numba.tests.test_sys_monitoring.TestMonitoring.test_start_event)
Traceback (most recent call last):
FAIL: test_stop_iteration_under_monitoring (numba.tests.test_sys_monitoring.TestMonitoring.test_stop_iteration_under_monitoring)
Traceback (most recent call last):
FAILED (failures=12, errors=1, skipped=1)
Traceback (most recent call last):
6ea4f842fb699a5cd34ec5bed98e259c47e02ca1 is the first bad commit
commit 6ea4f842fb699a5cd34ec5bed98e259c47e02ca1
Author: Sam Gross <colesbury@gmail.com>
Date:   Tue Mar 31 15:20:24 2026 -0400

    [3.14] gh-144438: Fix false sharing between QSBR and tlbc_index (gh-144554) (#144923)

    Align the QSBR thread state array to a 64-byte cache line boundary
    and add padding at the end of _PyThreadStateImpl. Depending on heap
    layout, the QSBR array could end up sharing a cache line with a
    thread's tlbc_index, causing QSBR quiescent state updates to contend
    with reads of tlbc_index in RESUME_CHECK. This is sensitive to
    earlier allocations during interpreter init and can appear or
    disappear with seemingly unrelated changes.

    Either change alone is sufficient to fix the specific issue, but both
    are worthwhile to avoid similar problems in the future.

    (cherry picked from commit 6577d870b0cb82baf540f4bcf49c01d68204e468)

 Doc/data/python3.14.abi                            | 3219 ++++++++++----------
 Include/internal/pycore_qsbr.h                     |    3 +-
 Include/internal/pycore_tstate.h                   |    5 +
 ...026-02-06-21-45-52.gh-issue-144438.GI_uB1LR.rst |    2 +
 Python/qsbr.c                                      |   20 +-
 5 files changed, 1653 insertions(+), 1596 deletions(-)
 create mode 100644 Misc/NEWS.d/next/Core_and_Builtins/2026-02-06-21-45-52.gh-issue-144438.GI_uB1LR.rst
bisect found first bad commit
```
