# Reproducer environment for numba/numba#10564 (TimingListener thread-safety)
#
# Uses the pypa manylinux image, which ships every supported CPython
# (including free-threaded variants) under /opt/python/<tag>-<abi>/.
# The free-threaded 3.14 build lives at:
#
#     /opt/python/cp314t-cp314t/bin/python3.14t
#
# BASE_IMAGE is overridden per-architecture by run.sh.
 
ARG BASE_IMAGE=quay.io/pypa/manylinux_2_28_x86_64
FROM ${BASE_IMAGE}
 
ENV PATH=/opt/python/cp314t-cp314t/bin:$PATH
 
# --only-binary :all: turns "no 3.14t wheel" into a hard failure rather
# than a silent attempt at a source build.
RUN python3.14t -m pip install --no-cache-dir \
        --only-binary :all: \
        numpy numba
 
WORKDIR /work
CMD ["bash"]
