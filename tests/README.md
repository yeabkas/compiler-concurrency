# ConcurrentLang Tests

This directory contains test files for the ConcurrentLang compiler and interpreter.

## Test Files

- `test_parser.py` - Tests for the parser and lexer
- `test_interpreter.py` - Tests for the interpreter/runtime
- `hello_parallel_ast.json` - Example AST output
- `hello_parallel_state.json` - Example runtime state output

## Running Tests

### With pytest (recommended)

```bash
pip install pytest
pytest tests/
```

### Run individual test files

```bash
python tests/test_parser.py
python tests/test_interpreter.py
```

### Run all tests with verbose output

```bash
pytest tests/ -v
```

## Writing New Tests

1. Create a new test file: `test_<feature>.py`
2. Import necessary modules from `concurrentlang`
3. Write test functions starting with `test_`
4. Use assertions to verify behavior

Example:
```python
def test_my_feature():
    """Test description."""
    parser_obj, lexer = parser_mod.build_parser()
    code = "int x = 0;"
    result = parser_obj.parse(code, lexer=lexer)
    assert isinstance(result, ast.Program)
```

## Test Coverage

To generate test coverage reports:

```bash
pip install pytest-cov
pytest tests/ --cov=concurrentlang --cov-report=html
```

View coverage report: `open htmlcov/index.html`
