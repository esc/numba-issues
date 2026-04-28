docker build -t numba-pr-10574 .
docker run --rm \
  -v ~/git/numba:/numba \
  -v $(pwd):/work \
  numba-pr-10574
