# .DEFAULT_GOAL := local
.PHONY: help
SHELL := /bin/bash

help:
	cat Makefile

update-gs-docs: sync-references

sync-references:
	bash skills/update-gs-docs/scripts/update-gs-docs.sh $(BRANCH)

sast-test:
	snyk auth $$SNYK_API_KEY
	snyk code test --severity-threshold=high --all-projects .
	snyk test --severity-threshold=high --all-projects .
