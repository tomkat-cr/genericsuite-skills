---
name: release-notes
description: Draft a new release changelog entry following the GenericSuite project conventions
disable-model-invocation: true
---

Help draft a new release changelog entry for the GenericSuite Basecamp project.

Steps:
1. Read an existing changelog file to understand the format, e.g. `docs/en/Releases/GS_Release_2025-02-20_Changelog.md`
2. Ask the user:
   - What is the release date? (YYYY-MM-DD)
   - What is the version number?
   - What are the main changes? (they can paste a list or describe them)
3. Classify each change as one of: `Add`, `Change`, `Fix`, `Remove`, `Security`
4. Draft the English changelog file at: `docs/en/Releases/GS_Release_{DATE}_Changelog.md`
5. Also draft the Spanish equivalent at: `docs/es/Releases/GS_Release_{DATE}_Changelog.md`
6. Remind the user to add entries to `mkdocs.yml` nav section and the releases index page

Follow the same heading structure, bullet style, and issue reference format (e.g., `[GS-NNN]`) as existing changelog files.
