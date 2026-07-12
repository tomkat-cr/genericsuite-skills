# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).


## [Unreleased] - Date

### Added

### Changed

### Fixed

### Removed

### Security


## 1.1.0 (2026-07-12)

### Added
- App-builder skill suite (`gs-app-builder-suite` plugin group) [GS-254]:
  `gs-app-builder` orchestrator (greenfield/brownfield mode detection, app-brief
  interview, checkpointed flow), `app-starter`, `config-builder` (updated),
  `jsx-code-builder` (updated), `menu-builder`, `endpoints-builder`,
  `python-fastapi-code-builder`, `python-ai-code-builder`,
  `python-ai-tools-code-builder`, `jsx-ai-code-builder`, `mcp-builder`.
- Per-skill `evals/evals.json` with runtime-validity assertions, exercised in
  `playground/` [GS-254].
- Reference-sync mechanism: `skills/update-gs-docs` map + script,
  `make sync-references` [GS-254].

### Changed
- Marketplace plugin group `code-generation-skills` renamed to
  `gs-app-builder-suite`; metadata version 1.1.0 [GS-254].
- README rewritten around the app-builder suite, installation and
  publishing [GS-254].


## [Unreleased] - 2026-04-12

### Added
- Project ideation and initial development [GS-254].
