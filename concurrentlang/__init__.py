"""Compatibility shim to allow imports like
`from concurrentlang.grammar import lexer` when project files live
as top-level packages (e.g. `grammar`, `runtime`, `ast`, `sem`).

This module preloads the common subpackages and registers
`concurrentlang.<pkg>` and `concurrentlang.<pkg>.<sub>` entries in
`sys.modules` so legacy imports in the repository continue to work.
"""
import sys
import os
import importlib.util
import types

# Ensure repo root (parent of this file) is first on sys.path so local
# folders like `grammar`, `runtime`, `ast`, `sem` are preferred over
# standard-library modules with the same names.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Map of project folders and the module files we want to expose under
# `concurrentlang.<pkg>.<sub>` so code that does
# `from concurrentlang.grammar import lexer` works even when the repo
# uses plain folders (no package __init__.py).
MAPPINGS = {
    'grammar': ['lexer', 'parser'],
    'runtime': ['interpreter', 'runtime', 'atomic'],
    'ast': ['nodes'],
    'sem': ['semantic', 'deadlock_detector', 'race_detector'],
}

for pkg, subs in MAPPINGS.items():
    pkg_mod = types.ModuleType(f'concurrentlang.{pkg}')
    # Mark as package by providing a __path__ so importlib treats it as one
    pkg_mod.__path__ = [os.path.join(ROOT, pkg)]
    # register package module early so submodules can import the package
    sys.modules[f'concurrentlang.{pkg}'] = pkg_mod
    added_any = False
    for sub in subs:
        candidate = os.path.join(ROOT, pkg, f'{sub}.py')
        if not os.path.isfile(candidate):
            continue
        name = f'concurrentlang.{pkg}.{sub}'
        spec = importlib.util.spec_from_file_location(name, candidate)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception:
            continue
        sys.modules[name] = mod
        setattr(pkg_mod, sub, mod)
        added_any = True
    if added_any:
        globals()[pkg] = pkg_mod

__all__ = list(MAPPINGS.keys())
