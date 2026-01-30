# Minimal interpreter/runtime for ConcurrentLang AST
# Place this at concurrentlang/runtime/interpreter.py

import threading
import queue
import contextlib
import time
from concurrentlang.ast import nodes as ast

class Channel:
    def __init__(self, maxsize=0):
        self.q = queue.Queue(maxsize=maxsize)
    def send(self, v):
        self.q.put(v)
    def recv(self, timeout=None):
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            raise RuntimeError("Channel receive timed out")

class Lock:
    def __init__(self):
        self._lock = threading.RLock()
    def acquire(self, timeout=None):
        if timeout is None:
            return self._lock.acquire()
        else:
            return self._lock.acquire(timeout=timeout)
    def release(self):
        self._lock.release()
    @contextlib.contextmanager
    def hold(self):
        self.acquire()
        try:
            yield
        finally:
            self.release()

# simple global atomic lock (note: Python has GIL; this is illustrative)
_global_atomic_lock = threading.RLock()
@contextlib.contextmanager
def atomic_block():
    _global_atomic_lock.acquire()
    try:
        yield
    finally:
        _global_atomic_lock.release()

class ThreadManager:
    def __init__(self):
        self.threads = []

    def spawn(self, fn, *args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.start()
        self.threads.append(t)
        return t

    def join_all(self):
        for t in self.threads:
            t.join()

class Interpreter:
    def __init__(self):
        # globals holds variables and channel/runtime objects
        self.globals = {}
        self.locks = {}  # string -> Lock()
        self.thread_manager = ThreadManager()

    def get_lock(self, name):
        if name not in self.locks:
            self.locks[name] = Lock()
        return self.locks[name]

    def exec_program(self, program: ast.Program):
        for stmt in program.statements:
            self.exec_stmt(stmt)
        # Wait for all spawned threads
        self.thread_manager.join_all()

    def exec_stmt(self, s):
        if isinstance(s, ast.VarDecl):
            init_val = self.eval_expr(s.init) if s.init is not None else 0
            self.globals[s.name] = init_val
        elif isinstance(s, ast.ChannelDecl):
            # For now ignore the element type; create an unbounded channel
            self.globals[s.name] = Channel()
        elif isinstance(s, ast.Assign):
            val = self.eval_expr(s.expr)
            self.globals[s.target.name] = val
        elif isinstance(s, ast.Send):
            ch = self.globals.get(s.chan.name)
            if ch is None:
                raise RuntimeError(f"Unknown channel: {s.chan.name}")
            val = self.eval_expr(s.value)
            ch.send(val)
        elif isinstance(s, ast.Recv):
            ch = self.globals.get(s.chan.name)
            if ch is None:
                raise RuntimeError(f"Unknown channel: {s.chan.name}")
            val = ch.recv()
            self.globals[s.target.name] = val
        elif isinstance(s, ast.ParallelBlock):
            # naive: spawn a thread per top-level statement inside the block
            for sub in s.statements:
                # capture sub in default arg to avoid late-binding
                self.thread_manager.spawn(lambda st=sub: self.exec_stmt(st))
        elif isinstance(s, ast.Spawn):
            # spawn an expression interpreted as a callable: for now, if expr is Identifier referencing a function (not implemented),
            # else if it's a literal or other expression we just evaluate it in a new thread.
            def run_expr():
                try:
                    self.eval_expr(s.expr)
                except Exception as e:
                    print("Spawned thread error:", e)
            self.thread_manager.spawn(run_expr)
        elif isinstance(s, ast.Lock):
            lk = self.get_lock(s.var.name)
            lk.acquire()
        elif isinstance(s, ast.Unlock):
            lk = self.get_lock(s.var.name)
            lk.release()
        elif isinstance(s, ast.Atomic):
            with atomic_block():
                for ss in s.statements:
                    self.exec_stmt(ss)
        else:
            raise NotImplementedError(f"Unimplemented exec for node type: {type(s)}")

    def eval_expr(self, e):
        if e is None:
            return None
        if isinstance(e, ast.Literal):
            return e.value
        if isinstance(e, ast.Identifier):
            # return value from globals (0 default)
            return self.globals.get(e.name, 0)
        # extend with arithmetic / function calls as needed
        raise NotImplementedError(f"Unimplemented eval for expression type: {type(e)}")