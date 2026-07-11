---
name: update-gs-docs
description: Sync reference files from the genericsuite-basecamp repository into the skills that bundle them (config-builder, menu-builder, endpoints-builder, python-fastapi-code-builder). Map-driven via reference_map.txt; run after basecamp docs or code examples change, or when adding a new skill that needs basecamp exemplars.
---

## Scripts

- `scripts/update-gs-docs.sh`: Map-driven sync of reference files from the
  `genericsuite-basecamp` repository into this repo's skills. The file list
  lives in `skills/update-gs-docs/reference_map.txt` (format:
  `<basecamp-relative-path>|<this-repo-relative-path>`, `#` comments allowed).
  If `BASECAMP_DIR` points to a local basecamp checkout (or
  `../genericsuite-basecamp` exists, as in the GenericSuite superproject), it
  copies locally; otherwise it downloads from GitHub raw on the branch given
  as first argument (default `develop`). Run it via `make sync-references`.
  When adding a new skill that needs basecamp exemplars, append lines to
  `reference_map.txt` and re-run — do not hand-copy files.
