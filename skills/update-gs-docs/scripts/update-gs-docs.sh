#!/usr/bin/env bash
# skills/update-gs-docs/scripts/update-gs-docs.sh
# 2026-04-11 | CR
# Update files required by the GenericSuite skills operations

download_file() {
  local url_index="$1"
  local dest_dir="$2"
  local dest_file="$3"
  local dest_filespec="$dest_dir/$dest_file"

  echo ""
  echo "Ensuring directory exists: $dest_dir"
  mkdir -p "$dest_dir"

  echo "Downloading index.md from develop branch..."
  curl -sSL "$url_index" -o "$dest_filespec"
  if [ $? -eq 0 ]; then
    echo "Successfully updated $dest_filespec"
  else
    echo "Failed to update $dest_filespec"
  fi  
}

# Get absolute path to the generic workspace root, assuming the script is run from anywhere within it
# To be safe, we'll navigate relative to this script or assume we run it from repo root.
# Getting repo root relative to the script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REPO_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"

cd "$REPO_ROOT" || exit 1

BRANCH="$1"
if [ "${BRANCH}" = "" ]; then
  BRANCH="develop"
fi

# Configuration guide main document
SOURCE_URL="https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/refs/heads/${BRANCH}/docs/en/Configuration-Guide/index.md"
DEST_DIR="skills/config-builder/gs_docs/en/Configuration-Guide"
DEST_FILE="index.md"

download_file "$SOURCE_URL" "$DEST_DIR" "$DEST_FILE"

# Configuration guide JSON config files document
SOURCE_URL="https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/refs/heads/${BRANCH}/docs/en/Configuration-Guide/Generic-CRUD-Editor-Configuration.md"
DEST_DIR="skills/config-builder/gs_docs/en/Configuration-Guide"
DEST_FILE="Generic-CRUD-Editor-Configuration.md"

download_file "$SOURCE_URL" "$DEST_DIR" "$DEST_FILE"

# Documentation to use the "new-project-from-template.sh" script
SOURCE_URL="https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/refs/heads/${BRANCH}/docs/code/fastapitemplate/README.md"
DEST_DIR="skills/config-builder/gs_docs/code/fastapitemplate"
DEST_FILE="README.md"

# JSON config files schema validator
SOURCE_URL="https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/refs/heads/${BRANCH}/docs/code/configuration-guide/crud_editor_config_classes.py"
DEST_DIR="skills/config-builder/gs_docs/code/configuration-guide"
DEST_FILE="crud_editor_config_classes.py"

download_file "$SOURCE_URL" "$DEST_DIR" "$DEST_FILE"

# Script to build a new monorepo project from a template
SOURCE_URL="https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/${BRANCH}/scripts/new-project-from-template.sh"
DEST_DIR="skills/config-builder/scripts"
DEST_FILE="new-project-from-template.sh"

download_file "$SOURCE_URL" "$DEST_DIR" "$DEST_FILE"

echo ""
echo "Documentation update complete."
