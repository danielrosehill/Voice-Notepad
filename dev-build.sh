#!/bin/bash
# Quick dev build - uses caching and skips compression
# Just run: ./dev-build.sh

exec ./build-install.sh --fast "$@"
