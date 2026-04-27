FROM python:3.14t-slim
RUN pip install numba pytest pytest-run-parallel
WORKDIR /app
COPY repro.py .
CMD ["pytest", "--parallel-threads=8", "repro.py"]
