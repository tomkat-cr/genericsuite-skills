#!/bin/bash
# scripts/new-project-from-template.sh
# Copies the fastapitemplate from the genericsuite-basecamp repo into a new
# directory and optionally renames it to start a fresh project.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/main/scripts/new-project-from-template.sh | bash
#       or
#   bash new-project-from-template.sh <target-dir> [<new-app-name>] [<new-domain>] [<template-name>]
#
# Examples:
#   bash new-project-from-template.sh ~/projects/myapp
#   bash new-project-from-template.sh ~/projects/myapp myapp
#   bash new-project-from-template.sh ~/projects/myapp myapp myapp.com
#   bash new-project-from-template.sh ~/projects/myapp myapp myapp.com exampleapp

set -e

export TARGET_DIR="$1"
export NEW_NAME="$2"
export NEW_DOMAIN="$3"
export TEMPLATE_NAME="$4"
export BASECAMP_BRANCH="$5"

clean_up() {
    echo ""
    echo "Cleaning up ${TMP_DIR}..."
    rm -rf "${TMP_DIR}"
}

# ── Introduction ───────────────────────────────────────────────────────────────

echo ""
echo "Create a new project from a GenericSuite template"
echo ""
echo "Copies a code template from the genericsuite-basecamp repo into a new"
echo "directory and optionally renames it to start a fresh project."

if [ -z "${TARGET_DIR}" ]; then
    echo ""
    echo "Enter target directory: "
    read TARGET_DIR < /dev/tty
fi
if [ -z "${NEW_NAME}" ]; then
    echo ""
    echo "Enter new app name: "
    read NEW_NAME < /dev/tty
fi
if [ -z "${NEW_DOMAIN}" ]; then
    echo ""
    echo "Enter new domain: "
    read NEW_DOMAIN < /dev/tty
fi
if [ -z "${TEMPLATE_NAME}" ]; then
    echo ""
    echo "Enter template name (default: fastapitemplate): "
    read TEMPLATE_NAME < /dev/tty
fi
if [ -z "${BASECAMP_BRANCH}" ]; then
    echo ""
    echo "Enter basecamp branch (default: main): "
    read BASECAMP_BRANCH < /dev/tty
fi

# ── Validation ───────────────────────────────────────────────────────────────

if [ -z "${TARGET_DIR}" ]; then
    echo ""
    echo "Usage: bash new-project-from-template.sh <target-dir> [<new-app-name>] [<new-domain>] [<template-name>]"
    echo "  target-dir   : destination directory for the new project"
    echo "  new-app-name : (optional) rename the app; lowercase letters, numbers and hyphens only"
    echo "  new-domain   : (optional) new domain, defaults to <new-app-name>.com"
    echo "  template-name: (optional) template name, defaults to fastapitemplate"
    echo "  basecamp-branch: (optional) basecamp branch, defaults to develop"
    echo ""
    exit 1
fi

if [ -e "${TARGET_DIR}" ]; then
    echo "Error: target directory already exists: ${TARGET_DIR}"
    echo ""
    exit 1
fi

if ! echo "${NEW_NAME}" | grep -qE '^[a-z0-9][a-z0-9-]*[a-z0-9]$'; then
    echo "Error: app name must contain only lowercase letters, numbers, and hyphens."
    echo "  Got: ${NEW_NAME}"
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo "Error: git is not installed."
    echo ""
    exit 1
fi

# ── Set defaults ───────────────────────────────────────────────────────────────

if [ -z "${TEMPLATE_NAME}" ]; then
    TEMPLATE_NAME="fastapitemplate"
fi
if [ -z "${BASECAMP_BRANCH}" ]; then
    BASECAMP_BRANCH="main"
fi

echo ""
echo "Target directory (TARGET_DIR): ${TARGET_DIR}"
echo "New project name (NEW_NAME): ${NEW_NAME}"
echo "New domain name (NEW_DOMAIN): ${NEW_DOMAIN}"
echo "Source template name (TEMPLATE_NAME): ${TEMPLATE_NAME}"
echo "Basecamp branch (BASECAMP_BRANCH): ${BASECAMP_BRANCH}"
echo ""

# ── Clone and copy ────────────────────────────────────────────────────────────

TMP_DIR="$(mktemp -d)"

BASECAMP_REPO="https://github.com/tomkat-cr/genericsuite-basecamp.git"
TEMPLATE_PATH="docs/code/${TEMPLATE_NAME}"

# trap 'rm -rf "$TMP_DIR"' EXIT
trap 'clean_up' EXIT

echo ""
echo "Cloning genericsuite-basecamp (shallow)..."
echo ""
git clone --depth 1 --branch "${BASECAMP_BRANCH}" --quiet "${BASECAMP_REPO}" "${TMP_DIR}"

echo "Copying template to ${TARGET_DIR} ..."
echo ""
cp -r "${TMP_DIR}/${TEMPLATE_PATH}" "${TARGET_DIR}"
mkdir -p "${TARGET_DIR}/scripts"
cp -r "${TMP_DIR}/scripts/rename-app.sh" "${TARGET_DIR}/scripts/rename-app.sh"

# echo "Cleaning up..."
# trap handles TMP_DIR removal on exit

# ── Initialize new git repo ──────────────────────────────────────────────────

echo "Initializing git repository..."
echo ""
cd "${TARGET_DIR}"
rm -rf .git
git init --quiet
git add .
git commit --quiet -m "Initial commit from ${TEMPLATE_NAME}"

# ── Optional rename ───────────────────────────────────────────────────────────

if [ -n "$NEW_NAME" ]; then
    echo ""
    RENAME_ARGS=("${NEW_NAME}")
    [ -n "${NEW_DOMAIN}" ] && RENAME_ARGS+=("${NEW_DOMAIN}")
    bash scripts/rename-app.sh "${RENAME_ARGS[@]}"

    echo "Committing rename..."
    echo ""
    git add .
    git commit --quiet -m "Rename: ${TEMPLATE_NAME} → ${NEW_NAME}"
fi

# ── Done ─────────────────────────────────────────────────────────────────────

echo ""
echo "Project ready at: ${TARGET_DIR}"
echo ""
echo "Next steps:"
echo "  cd ${TARGET_DIR}"
echo "  make init-app-environment   # copy .env.example → .env files"
echo "  nano .env                   # edit .env file"
echo "  make install-all            # install Node.js dependencies"
echo "  make dev                    # start development environment"
echo "  make run                    # start with Docker (local DB)"
