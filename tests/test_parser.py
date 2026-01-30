"""
Test suite for ConcurrentLang parser.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from concurrentlang.grammar import parser as parser_mod
from concurrentlang.ast import nodes as ast


def test_variable_declaration():
    """Test parsing simple variable declaration."""
    parser_obj, lexer = parser_mod.build_parser()
    code = "int x = 42;"
    result = parser_obj.parse(code, lexer=lexer)
    
    assert isinstance(result, ast.Program)
    assert len(result.statements) == 1
    assert isinstance(result.statements[0], ast.VarDecl)
    assert result.statements[0].name == "x"
    assert result.statements[0].typ == "int"


def test_channel_declaration():
    """Test parsing channel declaration."""
    parser_obj, lexer = parser_mod.build_parser()
    code = "chan<int> c;"
    result = parser_obj.parse(code, lexer=lexer)
    
    assert isinstance(result, ast.Program)
    assert len(result.statements) == 1
    assert isinstance(result.statements[0], ast.ChannelDecl)
    assert result.statements[0].name == "c"
    assert result.statements[0].typ == "int"


def test_parallel_block():
    """Test parsing parallel block."""
    parser_obj, lexer = parser_mod.build_parser()
    code = """
    int x = 0;
    parallel {
        int y = 1;
    }
    """
    result = parser_obj.parse(code, lexer=lexer)
    
    assert isinstance(result, ast.Program)
    assert len(result.statements) == 2
    assert isinstance(result.statements[1], ast.ParallelBlock)


def test_send_receive():
    """Test parsing send and receive operations."""
    parser_obj, lexer = parser_mod.build_parser()
    code = """
    chan<int> c;
    int x = 0;
    send(c, 42);
    x = recv(c);
    """
    result = parser_obj.parse(code, lexer=lexer)
    
    assert isinstance(result, ast.Program)
    assert len(result.statements) == 4
    assert isinstance(result.statements[0], ast.ChannelDecl)
    assert isinstance(result.statements[1], ast.VarDecl)
    assert isinstance(result.statements[2], ast.Send)
    assert isinstance(result.statements[3], ast.Recv)


def test_atomic_block():
    """Test parsing atomic block."""
    parser_obj, lexer = parser_mod.build_parser()
    code = """
    atomic {
        int x = 0;
    }
    """
    result = parser_obj.parse(code, lexer=lexer)
    
    assert isinstance(result, ast.Program)
    assert len(result.statements) == 1
    assert isinstance(result.statements[0], ast.Atomic)


if __name__ == "__main__":
    # Run tests
    test_variable_declaration()
    print("✓ Variable declaration test passed")
    
    test_channel_declaration()
    print("✓ Channel declaration test passed")
    
    test_parallel_block()
    print("✓ Parallel block test passed")
    
    test_send_receive()
    print("✓ Send/Receive test passed")
    
    test_atomic_block()
    print("✓ Atomic block test passed")
    
    print("\nAll tests passed!")
