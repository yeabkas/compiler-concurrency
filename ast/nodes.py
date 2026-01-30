# Simple AST node classes
class Node:
    pass

class Program(Node):
    def __init__(self, statements):
        self.statements = statements

class VarDecl(Node):
    def __init__(self, name, typ, init=None, shared=False):
        self.name = name
        self.typ = typ
        self.init = init
        self.shared = shared  # mark shared/global vars

class ChannelDecl(Node):
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ

class ParallelBlock(Node):
    def __init__(self, statements):
        self.statements = statements

class Spawn(Node):
    def __init__(self, expr):  # spawn(expression or function)
        self.expr = expr

class Lock(Node):
    def __init__(self, var):
        self.var = var

class Unlock(Node):
    def __init__(self, var):
        self.var = var

class Atomic(Node):
    def __init__(self, statements):
        self.statements = statements

class Send(Node):
    def __init__(self, chan, value):
        self.chan = chan
        self.value = value

class Recv(Node):
    def __init__(self, target, chan):
        self.target = target
        self.chan = chan

class Assign(Node):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

class Identifier(Node):
    def __init__(self, name):
        self.name = name

class Literal(Node):
    def __init__(self, value):
        self.value = value