# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).


## [Unreleased] - YYYY-MM-DD

### Added
- App-delivery skill suite (`gs-app-delivery-suite` plugin group) [GS-254]:
  `privacy-policy-checker` — compares an app's privacy policy against what the
  code actually collects, with a fixed data-inventory sweep (permissions, SDKs,
  AI/model providers, identity linkage, retention/consent), bundled Google Play
  Data Safety / Apple Privacy Nutrition Label + ATT / GDPR / CCPA / COPPA
  requirement references, an alignment matrix covering every inventory item,
  and patch-ready policy clause text [GS-254].
- `evals/evals.json` suite for `privacy-policy-checker`, exercised against a
  gap-rich fixture app in `playground/privacy-policy-check-test/` [GS-254].

### Changed
- Marketplace metadata version bumped to 1.2.0 for the new
  `gs-app-delivery-suite` plugin group [GS-254].

### Fixed

### Removed

### Security


## [1.0.0] - 2026-08-30

### Added
- Project ideation and initial development (2026-04-12) [GS-254].
- App-builder skill suite (`gs-app-builder-suite` plugin group) [GS-254]:
  `gs-app-builder` orchestrator (greenfield/brownfield mode detection, app-brief
  interview, checkpointed flow), `app-starter`, `config-builder` (updated),
  `jsx-code-builder` (updated), `menu-builder`, `endpoints-builder`,
  `python-fastapi-code-builder`, `python-ai-code-builder`,
  `python-ai-tools-code-builder`, `jsx-ai-code-builder`, `mcp-builder`.
- `evals/evals.json` suites (all suite skills except config-builder) with runtime-validity assertions, exercised in
  `playground/` [GS-254].
- Reference-sync mechanism: `skills/update-gs-docs` map + script,
  `make sync-references` [GS-254].
- Add SAST testing [GS-315].

### Changed
- Marketplace plugin group `code-generation-skills` renamed to
  `gs-app-builder-suite`; metadata version 1.1.0 [GS-254].
- README rewritten around the app-builder suite, installation and
  publishing [GS-254].

### Removed
- `release-notes` skill removed from marketplace, and delete SKILL.md file (moved to GS Superproject directory) [GS-191].

### Security
- Migrate to Python 3.14 [GS-337].
- Bump Node.js version in .nvmrc to 26 [GS-339].
