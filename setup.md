# ConcurrentLang Setup Guide

## Quick Setup

### 1. Prerequisites

Ensure you have the following installed:
- **Python 3.8+** (check with `python3 --version`)
- **pip** package manager
- **git** for version control

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yeabkas/compiler-concurrency.git
cd compiler-concurrency

# Create a virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Run the example program
python run_example.py

# You should see output like:
# === Parsed AST (summary) ===
# Program
# AST dumped to tests/hello_parallel_ast.json
# Interpreter finished.
# === Final globals ===
# ...
```

## Development Setup

### Install in Development Mode

```bash
pip install -e .
```

This allows you to edit the code and see changes immediately without reinstalling.

### Install Development Tools (Optional)

```bash
pip install pytest pytest-cov black flake8 mypy
```

## Troubleshooting

### PLY Not Found

If you see `ModuleNotFoundError: No module named 'ply'`:
```bash
pip install ply
```

### PYTHONPATH Issues

If imports fail, ensure you're running from the project root or add to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Virtual Environment Not Activated

Make sure you see `(.venv)` in your terminal prompt. If not:
```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

## Running Examples

### Basic Usage

```bash
# Run default example
python run_example.py

# Run specific file
python run_example.py --file examples/hello_parallel.cl

# Export AST and state
python run_example.py --dump-ast output/ast.json --dump-state output/state.json
```

### Creating Your Own Programs

1. Create a `.cl` file in the `examples/` directory
2. Write your ConcurrentLang code
3. Run with: `python run_example.py --file examples/your_file.cl`

## IDE Setup

### VS Code

Recommended extensions:
- Python (Microsoft)
- Pylance

Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.analysis.extraPaths": ["${workspaceFolder}"]
}
```

### PyCharm

1. Open project
2. Go to Settings → Project → Python Interpreter
3. Add virtual environment: `.venv/`
4. Mark `concurrentlang` directory as "Sources Root"

## Next Steps

- Read the [README.md](README.md) for language features
- Explore examples in `examples/`
- Check out the parser in `grammar/parser.py`
- Review AST nodes in `ast/nodes.py`
