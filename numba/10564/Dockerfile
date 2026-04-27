FROM quay.io/pypa/manylinux_2_28_x86_64
ENV PATH=/opt/python/cp314-cp314t/bin:$PATH
RUN pip install numba pytest pytest-run-parallel
WORKDIR /app
COPY repro.py .
CMD ["pytest", "--parallel-threads=8", "repro.py"]
