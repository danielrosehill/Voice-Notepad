#!/bin/bash
# Release script for Voice Notepad
# - Increments version (patch by default)
# - Takes screenshots
# - Builds .deb package
#
# Usage: ./release.sh [major|minor|patch]
#   Default: patch (1.3.0 -> 1.3.1)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep -Po '(?<=^version = ")[^"]+' pyproject.toml)
echo "Current version: $CURRENT_VERSION"

# Parse version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Determine bump type
BUMP_TYPE="${1:-patch}"

case "$BUMP_TYPE" in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo "Invalid bump type: $BUMP_TYPE"
        echo "Usage: ./release.sh [major|minor|patch]"
        exit 1
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
VERSION_UNDERSCORE="${MAJOR}_${MINOR}_${PATCH}"

echo "New version: $NEW_VERSION"
echo ""

# Update version in pyproject.toml
sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo "Updated pyproject.toml"

# Update version in build.sh
sed -i "s/^VERSION=\".*\"/VERSION=\"$NEW_VERSION\"/" build.sh
echo "Updated build.sh"

echo ""
echo "=== Taking Screenshots ==="
./take-screenshots.sh

echo ""
echo "=== Building Package ==="
./build.sh "$NEW_VERSION"

echo ""
echo "=== Release Complete ==="
echo "Version: $NEW_VERSION"
echo "Screenshots: screenshots/$VERSION_UNDERSCORE/"
echo "Package: dist/voice-notepad_${NEW_VERSION}_amd64.deb"
