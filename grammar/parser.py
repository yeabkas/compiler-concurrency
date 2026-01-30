import ply.yacc as yacc
from concurrentlang.grammar import lexer as lexmod
from concurrentlang.ast import nodes as ast

tokens = lexmod.tokens

precedence = (
    # Define precedences if you add operators later
)

def p_program(p):
    "program : statements"
    p[0] = ast.Program(p[1])

def p_statements_multiple(p):
    "statements : statements statement"
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    "statements : statement"
    p[0] = [p[1]]

# variable declaration: e.g., int x = 0;
def p_var_decl(p):
    "statement : INT ID ASSIGN expression SEMI"
    p[0] = ast.VarDecl(p[2], p[1], p[4])

def p_channel_decl(p):
    "statement : CHAN LT type GT ID SEMI"
    p[0] = ast.ChannelDecl(p[5], p[3])

def p_parallel_block(p):
    "statement : PARALLEL LBRACE statements RBRACE"
    p[0] = ast.ParallelBlock(p[3])

def p_spawn(p):
    "statement : SPAWN LPAREN expression RPAREN SEMI"
    p[0] = ast.Spawn(p[3])

def p_lock(p):
    "statement : LOCK LPAREN ID RPAREN SEMI"
    p[0] = ast.Lock(ast.Identifier(p[3]))

def p_unlock(p):
    "statement : UNLOCK LPAREN ID RPAREN SEMI"
    p[0] = ast.Unlock(ast.Identifier(p[3]))

def p_atomic(p):
    "statement : ATOMIC LBRACE statements RBRACE"
    p[0] = ast.Atomic(p[3])

def p_send(p):
    "statement : SEND LPAREN ID COMMA expression RPAREN SEMI"
    p[0] = ast.Send(ast.Identifier(p[3]), p[5])

def p_recv(p):
    "statement : ID ASSIGN RECV LPAREN ID RPAREN SEMI"
    p[0] = ast.Recv(ast.Identifier(p[1]), ast.Identifier(p[5]))

def p_assign(p):
    "statement : ID ASSIGN expression SEMI"
    p[0] = ast.Assign(ast.Identifier(p[1]), p[3])

def p_expression_literal(p):
    "expression : NUMBER"
    p[0] = ast.Literal(p[1])

def p_expression_id(p):
    "expression : ID"
    p[0] = ast.Identifier(p[1])

def p_type(p):
    "type : INT"
    p[0] = 'int'

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type}, value {p.value} (line {p.lineno})")
    else:
        print("Syntax error at EOF")

def build_parser():
    lex = lexmod.build_lexer()
    parser = yacc.yacc(module=__import__(__name__))
    return parser, lex

if __name__ == '__main__':
    parser, lex = build_parser()
    data = open('../examples/hello_parallel.cl').read()
    lex.input(data)
    result = parser.parse(data, lexer=lex)
    print(result)