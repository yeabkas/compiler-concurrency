# concurrentlang/sem/race_detector.py
from concurrentlang.ast import nodes

def collect_shared_vars(program: nodes.Program):
    shared = set()
    # any top-level var is considered shared for now
    for s in program.statements:
        if isinstance(s, nodes.VarDecl):
            shared.add(s.name)
    # any variable referenced inside a ParallelBlock is shared too
    def walk(stmts):
        for st in stmts:
            if isinstance(st, nodes.Assign):
                if isinstance(st.target, nodes.Identifier):
                    shared.add(st.target.name)
            elif isinstance(st, nodes.Recv):
                shared.add(st.target.name)
            elif isinstance(st, nodes.ParallelBlock):
                walk(st.statements)
            elif hasattr(st, "statements"):
                walk(getattr(st, "statements"))
    walk(program.statements)
    return shared

def find_unprotected_writes(program: nodes.Program):
    shared = collect_shared_vars(program)
    warnings = []

    def walk(stmts, locked=False, in_atomic=False):
        for st in stmts:
            if isinstance(st, nodes.Lock):
                locked = True
            elif isinstance(st, nodes.Unlock):
                locked = False
            elif isinstance(st, nodes.Atomic):
                # atomic protects inner statements
                walk(st.statements, locked=True, in_atomic=True)
            elif isinstance(st, nodes.Assign):
                if isinstance(st.target, nodes.Identifier):
                    name = st.target.name
                    if name in shared and not (locked or in_atomic):
                        warnings.append(f"Possible race: write to shared '{name}' outside lock/atomic")
            elif isinstance(st, nodes.ParallelBlock):
                # body runs concurrently => check its statements too
                walk(st.statements, locked=False, in_atomic=False)
            elif hasattr(st, "statements"):
                walk(getattr(st, "statements"), locked=locked, in_atomic=in_atomic)
    walk(program.statements)
    return warnings