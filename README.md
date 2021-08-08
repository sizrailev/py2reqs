# py2reqs
Utilities for navigating dependencies of Python scripts, modules, and packages.

## Pre-commit hooks
This project uses pre-commit hooks.
```shell
# Activate your Python virtual environment, for example:
source venv/bin/activate
# Install packages - see https://pre-commit.com
pip install -U pre-commit
# Set up the git pre-commit hooks
pre-commit install
```

## Tests
Run tests from the root folder containing `py2reqs` and `tests`tests with
```shell
python -m unittest
```
