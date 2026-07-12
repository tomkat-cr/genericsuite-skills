#!/bin/bash
# scripts/rename-app.sh
# Renames the app by replacing all occurrences of "fastapitemplate" (default old name)
# with a new name across config files, env examples, package descriptors, and
# docker compose files.
#
# Usage:
#   bash scripts/rename-app.sh <new-app-name> [<new-domain>] [<old-name>]
#
# Examples:
#   bash scripts/rename-app.sh myapp
#   bash scripts/rename-app.sh myapp myapp.com
#   bash scripts/rename-app.sh myapp myapp.com exampleapp

set -e

NEW_NAME="${1}"
NEW_DOMAIN="${2:-${NEW_NAME}.com}"
OLD_NAME="${3:-fastapitemplate}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$SCRIPT_DIR/.."

# ── Validation ──────────────────────────────────────────────────────────────

if [ -z "$NEW_NAME" ]; then
    echo "Usage: bash scripts/rename-app.sh <new-app-name> [<new-domain>] [<old-name>]"
    echo "  new-app-name : lowercase letters, numbers and hyphens only"
    echo "  new-domain   : defaults to <new-app-name>.com"
    echo "  old-name     : defaults to fastapitemplate"
    exit 1
fi

if ! echo "${NEW_NAME}" | grep -qE '^[a-z0-9][a-z0-9-]*[a-z0-9]$'; then
    echo "Error: app name must contain only lowercase letters, numbers, and hyphens."
    echo "  Got: ${NEW_NAME}"
    exit 1
fi

if [ "${NEW_NAME}" = "${OLD_NAME}" ]; then
    echo "Nothing to do — new name is the same as the current name (${OLD_NAME})."
    exit 0
fi

# ── File targets ─────────────────────────────────────────────────────────────

# Extensions/filenames to process
TARGET_PATTERNS=(
    "*.json"
    "*.toml"
    "*.yml"
    "*.yaml"
    "*.md"
    "*.sh"
    "*.conf"
    "*.example"
    "*.txt"
    "*.cfg"
    "*.js*"
    "*.mjs"
    "*.py"
    "*.html"
    "Makefile"
)

# Directories to skip
SKIP_DIRS=(
    ".git"
    "node_modules"
    "dist"
    "build"
    ".venv"
    "__pycache__"
    ".mypy_cache"
    ".pytest_cache"
)

# ── Build find command ────────────────────────────────────────────────────────

PRUNE_ARGS=()
for dir in "${SKIP_DIRS[@]}"; do
    PRUNE_ARGS+=(-path "*/${dir}" -o)
done
# Remove trailing -o
unset "PRUNE_ARGS[${#PRUNE_ARGS[@]}-1]"

NAME_ARGS=()
for i in "${!TARGET_PATTERNS[@]}"; do
    if [ $i -gt 0 ]; then
        NAME_ARGS+=(-o)
    fi
    NAME_ARGS+=(-name "${TARGET_PATTERNS[$i]}")
done

# ── Perform rename ────────────────────────────────────────────────────────────

echo ""
echo "Renaming '$OLD_NAME' → '$NEW_NAME'"
echo "Domain:  '${OLD_NAME}.com' → '$NEW_DOMAIN'"
echo "Base directory: $BASE_DIR"
echo ""

FILE_COUNT=0

while IFS= read -r -d '' file; do
    if grep -qiF "$OLD_NAME" "$file" 2>/dev/null; then
        # Replace domain first (more specific), then the plain app name
        perl -pi \
            -e "s/\Q${OLD_NAME}.com\E/${NEW_DOMAIN}/gi;" \
            -e "s/\Q${OLD_NAME}\E/${NEW_NAME}/gi;" \
            "$file"
        echo "  updated: ${file#$BASE_DIR/}"
        FILE_COUNT=$((FILE_COUNT + 1))
    fi
done < <(
    find "$BASE_DIR" \
        \( "${PRUNE_ARGS[@]}" \) -prune \
        -o -type f \( "${NAME_ARGS[@]}" \) -print0
)

echo ""
echo "Done. $FILE_COUNT file(s) updated."
echo ""
echo "Next steps:"
echo "  1. Run 'make init-app-environment' to copy the updated .env.example files."
echo "  2. Edit .env files and fill in your secrets."
echo "  3. Run 'npm run install:all' to install dependencies."
