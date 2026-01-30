# ConcurrentLang Compiler

A compiler and interpreter for ConcurrentLang, a programming language designed for concurrent and parallel programming with built-in support for:

- **Parallel execution blocks** with `parallel { }`
- **Channels** for inter-thread communication
- **Locks and atomic operations** for synchronization
- **Deadlock detection** - static analysis to detect potential deadlocks
- **Race condition detection** - identifies possible data races
- **Thread spawning** with `spawn()`

## Features

### Language Constructs

- **Variables**: `int x = 0;`
- **Channels**: `chan<int> c;` for typed message passing
- **Parallel blocks**: `parallel { ... }` to execute code in parallel
- **Send/Receive**: `send(c, 42);` and `recv(c, x);`
- **Locks**: `lock(m);` and `unlock(m);`
- **Atomic blocks**: `atomic { ... }` for atomic operations
- **Thread spawning**: `spawn(func);`

### Static Analysis

- **Semantic analysis** - type checking and scope validation
- **Deadlock detection** - identifies circular lock dependencies
- **Race condition detection** - detects unsynchronized shared variable access

### Code Generation

- **Interpreter** - direct execution of AST
- **LLVM backend** - compiles to LLVM IR (in progress)
- **JVM backend** - documentation for JVM bytecode generation

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yeabkas/compiler-concurrency.git
cd compiler-concurrency
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install the package in development mode:
```bash
pip install -e .
```

## Usage

### Running Examples

Run the default example:
```bash
python run_example.py
```

Run a specific `.cl` file:
```bash
python run_example.py --file examples/hello_parallel.cl
```

Dump AST and runtime state to JSON:
```bash
python run_example.py --dump-ast ast.json --dump-state state.json
```

### Example Program

```concurrentlang
int x = 0;
chan<int> c;
parallel {
  send(c, 42);
}
```

This creates an integer variable, a channel, and sends a value through the channel in a parallel block.

## Project Structure

```
├── ast/                    # Abstract Syntax Tree node definitions
│   └── nodes.py           # AST node classes
├── codegen/               # Code generation backends
│   ├── codegen_llvm.py   # LLVM IR generator
│   ├── codegen_jvm.md    # JVM bytecode docs
│   └── codegen_vm.md     # VM documentation
├── concurrentlang/        # Main package
│   └── __init__.py
├── examples/              # Example programs
│   └── hello_parallel.cl  # Basic parallel example
├── grammar/               # Lexer and parser
│   ├── lexer.py          # PLY lexer
│   └── parser.py         # PLY parser
├── runtime/               # Runtime system
│   ├── atomic.py         # Atomic operations
│   ├── interpreter.py    # AST interpreter
│   └── runtime.py        # Runtime support
├── sem/                   # Semantic analysis
│   ├── semantic.py       # Type checking
│   ├── deadlock_detector.py  # Deadlock detection
│   └── race_detector.py  # Race condition detection
├── tests/                 # Test files
├── run_example.py        # Main entry point
└── README.md
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Adding New Language Features

1. Update the lexer in `grammar/lexer.py` with new tokens
2. Update the parser in `grammar/parser.py` with new grammar rules
3. Add corresponding AST nodes in `ast/nodes.py`
4. Implement interpreter logic in `runtime/interpreter.py`
5. Add semantic checks in `sem/semantic.py` if needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built using PLY (Python Lex-Yacc) for parsing
- Inspired by Go's concurrency model and other concurrent languages