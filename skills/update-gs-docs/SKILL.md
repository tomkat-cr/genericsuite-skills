---
name: update-gs-docs
description: Skill to update the GenericSuite documentation files used by the `config-builder` skill.
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
