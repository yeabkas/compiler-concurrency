from concurrentlang.ast import nodes

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def declare(self, name, info):
        self.scopes[-1][name] = info

    def lookup(self, name):
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

def analyze(program: nodes.Program):
    st = SymbolTable()
    # Walk program and collect declarations
    for stmt in program.statements:
        if isinstance(stmt, nodes.VarDecl):
            st.declare(stmt.name, {'kind': 'var', 'type': stmt.typ, 'shared': stmt.shared})
        if isinstance(stmt, nodes.ChannelDecl):
            st.declare(stmt.name, {'kind': 'chan', 'type': stmt.typ})
    # More checks: uses, type checks, mark shared variables (those used in parallel)
    return st