#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CPYTHON_DIR=$(pwd)
CCACHE_DIR=${CCACHE_DIR:-$HOME/.ccache/bisect}
mkdir -p "$CCACHE_DIR"

docker run --rm \
    --platform linux/amd64 \
    -v "$CPYTHON_DIR:/cpython:ro" \
    -v "$CCACHE_DIR:/ccache" \
    cpython-bisect-base \
    bash /bisect_inner.sh 2>&1 | grep -E "^(==>|FAIL|ERROR|Traceback)"

exit ${PIPESTATUS[0]}
