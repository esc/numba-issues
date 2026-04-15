#!/bin/bash
set -e
PREFIX=/opt/testpython
PYTHON=$PREFIX/bin/python3.14

NPROC=$(nproc)
echo "==> Building CPython at $(git -C /cpython rev-parse --short HEAD)"
mkdir -p /build/cpython
rsync -a --exclude='.git' /cpython/ /build/cpython/
cd /build/cpython
./configure --prefix=$PREFIX --with-ensurepip=install 2>&1 | tail -5 || exit 125
make -j$NPROC 2>&1 | tail -10 || exit 125
make install 2>&1 | tail -5 || exit 125

echo "==> Installing Numba deps"
$PYTHON -m pip install numpy numba pytest || exit 125
echo "==> Running tests"
$PYTHON -m numba.runtests \
    numba.tests.test_sys_monitoring \
    numba.tests.test_profiler
