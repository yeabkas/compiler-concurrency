# Minimal PLY lexer for ConcurrentLang
import ply.lex as lex

# Reserved words
reserved = {
    'parallel': 'PARALLEL',
    'spawn': 'SPAWN',
    'lock': 'LOCK',
    'unlock': 'UNLOCK',
    'chan': 'CHAN',
    'send': 'SEND',
    'recv': 'RECV',
    'atomic': 'ATOMIC',
    'int': 'INT',      # example type
    'bool': 'BOOL',
}

tokens = [
    'ID', 'NUMBER', 'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN',
    'LT', 'GT', 'SEMI', 'COMMA', 'ASSIGN',
] + list(reserved.values())

# Token regexes
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LT = r'<'
t_GT = r'>'
t_SEMI = r';'
t_COMMA = r','
t_ASSIGN = r'='

t_ignore = ' \t\r'

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'//[^\n]*'
    pass

def t_error(t):
    print(f"Illegal character {t.value[0]!r} at line {t.lineno}")
    t.lexer.skip(1)

def build_lexer(**kwargs):
    return lex.lex(module=__import__(__name__), **kwargs)