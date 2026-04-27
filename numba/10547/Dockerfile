FROM python:3.14.4

# Compilers and dev tools (vim for in-container edits)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        vim \
    && rm -rf /var/lib/apt/lists/*

# numpy first — build + runtime dep for Numba
RUN pip install --no-cache-dir numpy setuptools

# llvmlite dev wheel from numba/label/dev on anaconda.org
# (--pre allows pre-release version specifiers; --extra-index-url keeps PyPI as fallback)
RUN pip install --no-cache-dir --pre \
        --extra-index-url https://pypi.anaconda.org/numba/label/dev/simple/ \
        llvmlite

WORKDIR /numba

CMD ["/bin/bash"]
