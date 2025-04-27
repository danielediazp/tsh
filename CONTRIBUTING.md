# Contributing

Thank you for your interest in contributing to Task Shell (tsh)! Follow the steps below to set up your development environment.

## Prerequisites

1. **Python Version**  
   Ensure you are using Python 3.13. It is recommended to use a Python version manager like `pyenv` to manage your Python versions.

   ```bash
   pyenv install 3.13
   pyenv local 3.13
   ```
2. **Virtual environment** to isolate dependencies

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies**

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

   ```bash
   pip install uv
   uv sync
   ```

## Code Style

Our project uses [Black](https://black.readthedocs.io/en/stable/index.html) for code formatting. Ensure your code is formatted before committing changes. Pre-commit hooks will also enforce this.

### Setup Pre-commits

Install and configure pre-commit hooks:

   ```bash
   pip install pre-commit
   pre-commit install
   ```


## Running the application

   ```bash
   uv run src/main.py # from root
   ```

## Running Tests

Run unit tests using `pytest`:

   ```bash
   pytest test
   ```

### Submitting Changes

TODO: update later to fork