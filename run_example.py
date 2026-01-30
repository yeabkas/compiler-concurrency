#!/usr/bin/env python3
"""
run_example.py

Usage:
  python run_example.py [--file examples/hello_parallel.cl] [--dump-ast ast.json] [--dump-state state.json]

This script:
 - builds the PLY parser/lexer (expects concurrentlang.grammar.parser.build_parser)
 - parses the input .cl file into an AST
 - prints a short AST summary to stdout
 - runs the interpreter (expects concurrentlang.runtime.interpreter.Interpreter)
 - optionally writes AST or final runtime state to JSON files
"""
import argparse
import json
from pathlib import Path

def ast_to_simple(obj):
    """Convert AST nodes to serializable dicts (simple heuristic)."""
    try:
        # If node has __dict__, convert fields recursively
        if hasattr(obj, '__dict__'):
            d = {'_type': obj.__class__.__name__}
            for k, v in obj.__dict__.items():
                if isinstance(v, list):
                    d[k] = [ast_to_simple(i) for i in v]
                else:
                    d[k] = ast_to_simple(v)
            return d
        # lists / tuples
        if isinstance(obj, (list, tuple)):
            return [ast_to_simple(i) for i in obj]
        # primitive
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        # fallback to repr
        return repr(obj)
    except Exception:
        return repr(obj)

def main():
    parser = argparse.ArgumentParser(description="Parse and run a ConcurrentLang example")
    parser.add_argument("--file", "-f", type=str, default="examples/hello_parallel.cl",
                        help="Path to .cl source file (default: examples/hello_parallel.cl)")
    parser.add_argument("--dump-ast", type=str, default=None,
                        help="Optional path to write AST as JSON")
    parser.add_argument("--dump-state", type=str, default=None,
                        help="Optional path to write final interpreter state as JSON")
    args = parser.parse_args()

    src_path = Path(args.file)
    if not src_path.exists():
        print(f"Error: source file not found: {src_path}")
        return

    # Import parser factory and interpreter from the package
    try:
        from concurrentlang.grammar import parser as parser_mod
        from concurrentlang.runtime.interpreter import Interpreter
    except Exception as e:
        print("Error importing concurrentlang modules. Make sure your package files exist and PYTHONPATH includes the repo root.")
        print("Import error:", e)
        return

    # Build parser and lexer
    try:
        parser_obj, lexer = parser_mod.build_parser()
    except Exception as e:
        print("Error building parser/lexer:", e)
        return

    # Read source and parse
    src = src_path.read_text(encoding='utf-8')
    try:
        ast_root = parser_obj.parse(src, lexer=lexer)
    except Exception as e:
        print("Parse error:", e)
        return

    # Print a simple AST summary
    print("=== Parsed AST (summary) ===")
    print(type(ast_root).__name__)
    # Optionally pretty dump to JSON
    if args.dump_ast:
        try:
            serial = ast_to_simple(ast_root)
            with open(args.dump_ast, 'w', encoding='utf-8') as f:
                json.dump(serial, f, indent=2)
            print(f"AST dumped to {args.dump_ast}")
        except Exception as e:
            print("Failed to dump AST:", e)
    else:
        # minimal textual print
        try:
            import pprint
            pprint.pprint(ast_to_simple(ast_root))
        except Exception:
            print(repr(ast_root))

    # Run interpreter
    try:
        interp = Interpreter()
        interp.exec_program(ast_root)
        print("Interpreter finished.")
        # show final global state if available
        if hasattr(interp, "globals"):
            print("=== Final globals ===")
            import pprint
            pprint.pprint(interp.globals)
            if args.dump_state:
                with open(args.dump_state, 'w', encoding='utf-8') as f:
                    json.dump(interp.globals, f, indent=2)
                print(f"Final state dumped to {args.dump_state}")
    except Exception as e:
        print("Interpreter error:", e)

if __name__ == "__main__":
    main()