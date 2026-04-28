FROM quay.io/pypa/manylinux_2_28_x86_64
ENV PATH=/opt/python/cp314-cp314t/bin:$PATH

RUN pip install --no-cache-dir setuptools wheel numpy pytest pytest-run-parallel

# llvmlite dev wheel from numba/label/dev on anaconda.org
RUN pip install --no-cache-dir --pre \
        --extra-index-url https://pypi.anaconda.org/numba/label/dev/simple/ \
        llvmlite

WORKDIR /work

CMD pip install --no-build-isolation -e /numba && PYTHON_GIL=0 pytest -vv repro_pytest.py --parallel-threads 4
