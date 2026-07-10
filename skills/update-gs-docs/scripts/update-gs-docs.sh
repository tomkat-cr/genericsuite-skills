#!/bin/bash
# skills/update-gs-docs/scripts/update-gs-docs.sh
# Map-driven sync of reference files from genericsuite-basecamp into the
# skills' references/ (and legacy gs_docs/) directories.
#
# Usage:
#   bash skills/update-gs-docs/scripts/update-gs-docs.sh [branch]
#   BASECAMP_DIR=/path/to/genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh
#
# Modes:
#   - If BASECAMP_DIR is set (or ../genericsuite-basecamp exists), copy files
#     from the local checkout (fast, works offline).
#   - Otherwise download each file from GitHub raw on the given branch
#     (default: develop).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REPO_ROOT="$(dirname "$(dirname "$(dirname "${SCRIPT_DIR}")")")"
MAP_FILE="${REPO_ROOT}/skills/update-gs-docs/reference_map.txt"

BRANCH="${1:-develop}"
BASECAMP_DIR="${BASECAMP_DIR:-}"
RAW_BASE="https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/refs/heads/${BRANCH}"

if [ -z "${BASECAMP_DIR}" ] && [ -d "${REPO_ROOT}/../genericsuite-basecamp" ]; then
    BASECAMP_DIR="${REPO_ROOT}/../genericsuite-basecamp"
fi

if [ ! -f "${MAP_FILE}" ]; then
    echo "Error: map file not found: ${MAP_FILE}"
    exit 1
fi

changed=0
unchanged=0
failed=0

while IFS='|' read -r src dest; do
    # Skip comments and blank lines
    case "${src}" in
        \#*|"") continue ;;
    esac
    dest_path="${REPO_ROOT}/${dest}"
    mkdir -p "$(dirname "${dest_path}")"
    tmp_file="$(mktemp)"
    if [ -n "${BASECAMP_DIR}" ]; then
        if ! cp "${BASECAMP_DIR}/${src}" "${tmp_file}" 2>/dev/null; then
            echo "FAILED (local copy): ${src}"
            failed=$((failed + 1))
            rm -f "${tmp_file}"
            continue
        fi
    else
        if ! curl -fsSL "${RAW_BASE}/${src}" -o "${tmp_file}"; then
            echo "FAILED (download): ${src}"
            failed=$((failed + 1))
            rm -f "${tmp_file}"
            continue
        fi
    fi
    if [ -f "${dest_path}" ] && cmp -s "${tmp_file}" "${dest_path}"; then
        unchanged=$((unchanged + 1))
        rm -f "${tmp_file}"
    else
        mv "${tmp_file}" "${dest_path}"
        echo "CHANGED: ${dest}"
        changed=$((changed + 1))
    fi
done < "${MAP_FILE}"

echo ""
echo "Reference sync complete: ${changed} changed, ${unchanged} unchanged, ${failed} failed."
if [ "${failed}" -gt 0 ]; then
    exit 1
fi
