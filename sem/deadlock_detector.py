from collections import defaultdict

def build_lock_graph(program):
    edges = defaultdict(set)

    def scan_block(stmts, held=None):
        if held is None: held = []
        i = 0
        while i < len(stmts):
            s = stmts[i]
            if s.__class__.__name__ == 'Lock':
                # subsequent locks in the same block form ordering
                held2 = held + [s.var.name]
                # add edges held -> new
                for h in held:
                    edges[h].add(s.var.name)
                # scan inner statements if any - assume lock scope may include following statements until unlock
                # naive: scan following statements until Unlock(s.var)
                j = i+1
                inner = []
                while j < len(stmts):
                    if stmts[j].__class__.__name__ == 'Unlock' and getattr(stmts[j].var,'name','')==s.var.name:
                        break
                    inner.append(stmts[j])
                    j += 1
                scan_block(inner, held2)
                i = j+1
                continue
            elif hasattr(s, 'statements'):
                scan_block(s.statements, held)
            i += 1

    scan_block(program.statements)
    return edges

def has_cycle(edges):
    visited = {}
    def dfs(n):
        if n in visited:
            return visited[n] == 1
        visited[n] = 1
        for m in edges.get(n, []):
            if dfs(m):
                return True
        visited[n] = 2
        return False

    for node in edges:
        if node not in visited:
            if dfs(node):
                return True
    return False