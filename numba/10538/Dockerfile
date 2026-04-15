FROM --platform=linux/amd64 python:3.14.4-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Numba and deps via pip (no conda on 3.14 yet)
RUN pip install --upgrade pip && \
    pip install \
        numpy \
        numba \
        pytest

WORKDIR /work

CMD ["/bin/bash"]
