#!/usr/bin/env bash
set -e
source .venv/bin/activate
uv run python experiments/sanity_check.py

