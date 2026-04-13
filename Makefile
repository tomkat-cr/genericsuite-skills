# .DEFAULT_GOAL := local
.PHONY: help
SHELL := /bin/bash

help:
	cat Makefile

update-gs-docs:
	bash skills/update-gs-docs/scripts/update-gs-docs.sh
