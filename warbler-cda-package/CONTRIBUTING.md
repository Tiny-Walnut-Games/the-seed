# Contributing to Warbler CDA

Thank you for your interest in contributing to Warbler CDA!

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://gitlab.com/tiny-walnut-games/the-seed.git
   cd the-seed/warbler-cda-package
   ```

2. Run setup:

   ```bash
   ./setup.sh
   ```

3. Install development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=warbler_cda --cov-report=html

# Run specific test
pytest tests/test_retrieval_api.py -v
```

## Code Style

We use:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black warbler_cda/

# Lint
flake8 warbler_cda/

# Type check
mypy warbler_cda/
```

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a merge request

## Questions?

Open an issue on GitLab: <https://gitlab.com/tiny-walnut-games/the-seed/-/issues>
