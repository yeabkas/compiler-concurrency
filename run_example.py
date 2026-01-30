# run_example.py
from concurrentlang.grammar import parser as parser_mod
from concurrentlang.runtime.interpreter import Interpreter
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    examples_dir = project_root / 'examples'
    example_file = examples_dir / 'hello_parallel.cl'
    parser, lex = parser_mod.build_parser()
    data = example_file.read_text()
    parsed = parser.parse(data, lexer=lex)
    print("Parsed AST:", parsed)
    interp = Interpreter()
    interp.exec_program(parsed)

if __name__ == "__main__":
    main()