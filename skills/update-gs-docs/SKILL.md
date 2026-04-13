---
name: update-gs-docs
description: Skill to update the GenericSuite documentation files used by the `config-builder` skill.
---

## Scripts

- `scripts/update-gs-docs.sh`: Downloads the expected documentation Markdown files directly from the `genericsuite-basecamp` repository. It grabs the `index.md` from the `develop` branch and `Generic-CRUD-Editor-Configuration.md` from the `main` branch, saving them to `skills/config-builder/gs_docs/en/Configuration-Guide/`.
