from concurrentlang.ast import nodes

def find_races(program):
    warnings = []
    def walk_statements(stmts, in_locked=False):
        for s in stmts:
            if isinstance(s, nodes.Lock):
                in_locked = True
            elif isinstance(s, nodes.Unlock):
                in_locked = False
            elif isinstance(s, nodes.Assign):
                # if target is a global/shared var and not in_locked -> warning
                if isinstance(s.target, nodes.Identifier):
                    name = s.target.name
                    # naive check: assume globals are shared (could refine)
                    if not in_locked:
                        warnings.append(f"Write to '{name}' without lock at assign")
            elif isinstance(s, nodes.ParallelBlock):
                # check body recursively; mark accesses in parall blocks as shared
                walk_statements(s.statements, in_locked)
            elif isinstance(s, nodes.Atomic):
                # atomic body: skip checks
                pass
    walk_statements(program.statements)
    return warnings