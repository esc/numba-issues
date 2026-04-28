docker build --platform=linux/amd64 -t numba-repro .
docker run --platform=linux/amd64 numba-repro
