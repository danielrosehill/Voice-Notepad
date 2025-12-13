#!/bin/bash
# Build and install Voice Notepad V3 in one step
# Combines build.sh and install.sh
#
# Usage: ./build-install.sh [VERSION] [--fast]
#   --fast: Skip compression for faster builds (good for dev iteration)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Pass all arguments to build.sh
BUILD_ARGS=("$@")

# Default version if none provided
if [ $# -eq 0 ] || [[ "$1" == --* ]]; then
    BUILD_ARGS=("1.1.0" "${BUILD_ARGS[@]}")
fi

echo "=== Voice Notepad V3 - Build & Install ==="
echo ""

# Build the package
./build.sh "${BUILD_ARGS[@]}"

# Install it
./install.sh

echo "=== Done ==="
