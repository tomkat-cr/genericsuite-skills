# .DEFAULT_GOAL := local
.PHONY: help
SHELL := /bin/bash

help:
	cat Makefile

update-gs-docs:
	bash skills/update-gs-docs/scripts/update-gs-docs.sh

sast-test:
	snyk code test --severity-threshold=high --all-projects .
	snyk test --severity-threshold=high --all-projects .

agents_md_link:
	ln -s CLAUDE.md AGENTS.md
