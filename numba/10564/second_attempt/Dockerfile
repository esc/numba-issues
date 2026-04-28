FROM quay.io/pypa/manylinux_2_28_x86_64
ENV PATH=/opt/python/cp314-cp314t/bin:$PATH
RUN pip install numba
WORKDIR /app
COPY repro_no_pytest.py .
CMD PYTHON_GIL=0 python repro_no_pytest.py && PYTHON_GIL=1 python repro_no_pytest.py
