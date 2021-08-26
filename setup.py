#!/usr/bin/env python3
from setuptools import setup

# This should be enabled by pyproject.toml, but that doesn't seem
# to work with pip 21.2.4.
setup(use_scm_version={"write_to": "src/rad/_version.py"})
