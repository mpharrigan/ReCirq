#!/bin/env bash

set -e
python dev_tools/write-ci-requirements.py --all-extras
pip-compile --output-file=ci-requirements-compiled.txt --resolver=backtracking ci-requirements.txt dev-requirements.txt
pip-sync ci-requirements-compiled.txt