#!/usr/bin/env bash
# Build (if needed) and launch the docker reproducer for numba/numba#10564.
#
# Usage:
#   ./run.sh                              # default: --mode=direct
#   ./run.sh --mode=both -t 64 -n 5000    # extra args go to repro_10564.py
#   ./run.sh --mode=compile -t 32 -n 200  # real compile workload
#
# Environment knobs:
#   PYTHON_GIL=1 ./run.sh        leave the GIL on (sanity / control run)
#   PLATFORM=linux/amd64 ./run.sh  cross-arch (slow under qemu emulation)
#   REBUILD=1 ./run.sh           force a rebuild of the docker image
#   DROP_TO_SHELL=1 ./run.sh     bash inside the container instead of the harness

set -euo pipefail

IMAGE=numba-10564
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# Pick the manylinux base image for the host arch (or the override platform).
case "$(uname -m)" in
    x86_64|amd64)  ARCH=x86_64 ;;
    aarch64|arm64) ARCH=aarch64 ;;
    *) echo "unsupported host arch: $(uname -m)" >&2; exit 1 ;;
esac

PLATFORM_FLAGS=()
if [[ -n "${PLATFORM:-}" ]]; then
    PLATFORM_FLAGS=(--platform "$PLATFORM")
    case "$PLATFORM" in
        */amd64|amd64)   ARCH=x86_64 ;;
        */arm64|arm64)   ARCH=aarch64 ;;
        *) echo "unsupported PLATFORM: $PLATFORM" >&2; exit 1 ;;
    esac
fi

BASE_IMAGE="quay.io/pypa/manylinux_2_28_${ARCH}"

if [[ "${REBUILD:-0}" == "1" ]] \
   || ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker build ${PLATFORM_FLAGS[@]+"${PLATFORM_FLAGS[@]}"} \
        --build-arg "BASE_IMAGE=$BASE_IMAGE" \
        -t "$IMAGE" "$DIR"
fi

TTY_FLAGS=()
if [ -t 0 ] && [ -t 1 ]; then
    TTY_FLAGS=(-it)
fi

DOCKER_RUN=(
    docker run --rm
    ${TTY_FLAGS[@]+"${TTY_FLAGS[@]}"}
    ${PLATFORM_FLAGS[@]+"${PLATFORM_FLAGS[@]}"}
    -e PYTHON_GIL="${PYTHON_GIL:-0}"
    -v "$DIR":/work:ro
    -w /work
    "$IMAGE"
)

if [[ "${DROP_TO_SHELL:-0}" == "1" ]]; then
    exec "${DOCKER_RUN[@]}" bash
else
    exec "${DOCKER_RUN[@]}" python3.14t repro_10564.py "$@"
fi
