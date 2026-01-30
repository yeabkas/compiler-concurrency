"""
Test suite for ConcurrentLang interpreter.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from concurrentlang.grammar import parser as parser_mod
from concurrentlang.runtime.interpreter import Interpreter


def test_simple_variable():
    """Test interpreting simple variable assignment."""
    parser_obj, lexer = parser_mod.build_parser()
    code = "int x = 42;"
    ast = parser_obj.parse(code, lexer=lexer)
    
    interp = Interpreter()
    interp.exec_program(ast)
    
    assert "x" in interp.globals
    assert interp.globals["x"] == 42


def test_channel_creation():
    """Test creating a channel."""
    parser_obj, lexer = parser_mod.build_parser()
    code = "chan<int> c;"
    ast = parser_obj.parse(code, lexer=lexer)
    
    interp = Interpreter()
    interp.exec_program(ast)
    
    assert "c" in interp.globals
    from concurrentlang.runtime.interpreter import Channel
    assert isinstance(interp.globals["c"], Channel)


def test_parallel_with_send():
    """Test parallel block with channel send."""
    parser_obj, lexer = parser_mod.build_parser()
    code = """
    chan<int> c;
    parallel {
        send(c, 42);
    }
    """
    ast = parser_obj.parse(code, lexer=lexer)
    
    interp = Interpreter()
    interp.exec_program(ast)
    
    assert "c" in interp.globals
    # Channel should have received the value
    from concurrentlang.runtime.interpreter import Channel
    assert isinstance(interp.globals["c"], Channel)


if __name__ == "__main__":
    # Run tests
    test_simple_variable()
    print("✓ Simple variable test passed")
    
    test_channel_creation()
    print("✓ Channel creation test passed")
    
    test_parallel_with_send()
    print("✓ Parallel with send test passed")
    
    print("\nAll interpreter tests passed!")
