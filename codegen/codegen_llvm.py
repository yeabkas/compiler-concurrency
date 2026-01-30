"""
Simple LLVM IR text code generator for the ConcurrentLang AST.

This generator produces a textual LLVM module (module.ll) in the "test" folder
(or in the folder given by output_path). It's a pragmatic, minimal lowering that:

- Emits global i64 variables for `int` VarDecls
- Emits placeholder globals for channels
- Emits a `@main` function containing the top-level statements
- Lowers `assign` (literal -> store) into simple LLVM store instructions
- Lowers `send` / `recv` into calls to declared runtime intrinsics:
    declare void @chan_send(i64* %chan, i64 %val)
    declare i64  @chan_recv(i64* %chan)
- Lowers `parallel` blocks and `spawn` into separate functions (stubs).
- Lowers `lock`/`unlock` and `atomic` into calls to declared runtime helpers:
    declare void @lock_acquire(i8* %lock)
    declare void @lock_release(i8* %lock)
    declare void @atomic_enter()
    declare void @atomic_exit()
- Produces a readable .ll file; it is intentionally conservative and *not*
  a full/production-quality LLVM codegen. It aims to be useful as a first pass
  and to generate inspectable IR in the repo's test/ folder.

Usage:
    from concurrentlang.codegen.codegen_llvm import generate_module
    generate_module(ast_root)                 # writes ./test/module.ll
    generate_module(ast_root, output_path="outdir")  # writes outdir/module.ll
"""

import os
from concurrentlang.ast import nodes

# Simple name sanitization for LLVM identifiers
def llvm_ident(name: str) -> str:
    # LLVM global identifiers may contain many characters but to be safe:
    return "".join(c if c.isalnum() or c == '_' else '_' for c in name)

class LLVMEmitter:
    def __init__(self):
        self.lines = []
        self.decls = set()
        self.func_counter = 0
        self.parallel_counter = 0
        self.spawn_counter = 0
        self.used_globals = set()

    def emit(self, line=""):
        self.lines.append(line)

    def declare(self, decl_line):
        if decl_line not in self.decls:
            self.decls.add(decl_line)

    def header(self):
        self.emit("; ModuleID = 'concurrent_module'")
        self.emit("source_filename = \"concurrentlang\"")
        self.emit("")

        # runtime declarations (placeholders)
        self.declare("declare void @chan_send(i64* %chan, i64 %val)")
        self.declare("declare i64 @chan_recv(i64* %chan)")
        self.declare("declare void @lock_acquire(i8* %lock)")
        self.declare("declare void @lock_release(i8* %lock)")
        self.declare("declare void @atomic_enter()")
        self.declare("declare void @atomic_exit()")

    def emit_declarations(self):
        for d in sorted(self.decls):
            self.emit(d)
        if self.decls:
            self.emit("")

    def emit_global_var(self, varname: str, typ: str):
        # Only int currently supported -> i64
        name = llvm_ident(varname)
        if name in self.used_globals:
            return
        self.used_globals.add(name)
        if typ == 'int':
            self.emit(f"@{name} = global i64 0")
        else:
            # fallback
            self.emit(f"@{name} = global i64 0 ; unknown type {typ}, emitted as i64")

    def emit_channel(self, channame: str):
        name = "chan_" + llvm_ident(channame)
        if name in self.used_globals:
            return
        self.used_globals.add(name)
        # Represent channel as i64* placeholder (actual runtime provides layout)
        self.emit(f"@{name} = global i64* null ; channel placeholder")

    def new_function_name(self, prefix="fn"):
        self.func_counter += 1
        return f"{prefix}_{self.func_counter}"

    def lower_program(self, prog: nodes.Program):
        # Scan declarations first to emit globals
        for stmt in prog.statements:
            if isinstance(stmt, nodes.VarDecl):
                self.emit_global_var(stmt.name, stmt.typ)
            elif isinstance(stmt, nodes.ChannelDecl):
                self.emit_channel(stmt.name)

        # Emit header (runtime decls)
        self.header()
        self.emit_declarations()

        # Lower parallel blocks and other helpers into separate functions
        # and lower top-level into main
        self.emit("define i32 @main() {")
        self.emit("entry:")
        # We will generate trivial IR: a linear sequence of operations and finally "ret i32 0"
        for stmt in prog.statements:
            for l in self.lower_statement(stmt, parent_context="main"):
                self.emit("  " + l)
        self.emit("  ret i32 0")
        self.emit("}")
        self.emit("")

    def lower_statement(self, stmt, parent_context):
        """
        Returns list of IR instruction lines (without indentation) for the given statement.
        parent_context is the current function name (used when creating helper functions).
        """
        out = []
        # Variable declaration with initializer: handled as global; initialization here will store initial value
        if isinstance(stmt, nodes.VarDecl):
            if stmt.init and isinstance(stmt.init, nodes.Literal):
                name = llvm_ident(stmt.name)
                out.append(f"; initialize @{name} with literal {stmt.init.value}")
                out.append(f"store i64 {int(stmt.init.value)}, i64* @{name}")
        elif isinstance(stmt, nodes.Assign):
            # Only handle Identifier <- Literal for now
            tgt = stmt.target
            expr = stmt.expr
            if isinstance(tgt, nodes.Identifier) and isinstance(expr, nodes.Literal):
                name = llvm_ident(tgt.name)
                out.append(f"; assign {expr.value} to @{name}")
                out.append(f"store i64 {int(expr.value)}, i64* @{name}")
            else:
                out.append(f"; assign: complex expr not lowered (target={type(tgt).__name__}, expr={type(expr).__name__})")
        elif isinstance(stmt, nodes.ChannelDecl):
            # already emitted as global
            out.append(f"; channel decl {stmt.name}")
        elif isinstance(stmt, nodes.Send):
            # send(chan, expr)
            chan = stmt.chan
            val = stmt.value
            if isinstance(chan, nodes.Identifier) and isinstance(val, nodes.Literal):
                chan_g = "chan_" + llvm_ident(chan.name)
                out.append(f"; send {val.value} to @{chan_g}")
                out.append(f"call void @chan_send(i64* @{chan_g}, i64 {int(val.value)})")
            else:
                out.append("; send: non-literal or complex send not lowered")
        elif isinstance(stmt, nodes.Recv):
            # recv target = recv(chan)
            if isinstance(stmt.chan, nodes.Identifier) and isinstance(stmt.target, nodes.Identifier):
                chan_g = "chan_" + llvm_ident(stmt.chan.name)
                tgt = llvm_ident(stmt.target.name)
                out.append(f"; recv into @{tgt} from @{chan_g}")
                out.append(f"%recv_tmp = call i64 @chan_recv(i64* @{chan_g})")
                out.append(f"store i64 %recv_tmp, i64* @{tgt}")
            else:
                out.append("; recv: complex pattern not lowered")
        elif isinstance(stmt, nodes.ParallelBlock):
            # create a helper function for the block and call it (no real threading here)
            self.parallel_counter += 1
            fname = f"parallel_block_{self.parallel_counter}"
            out.append(f"; parallel block -> call @{fname} (stubbed sequentially)")
            out.append(f"call void @{fname}()")
            # emit the function definition after main
            self.emit("")  # blank line separator
            self.emit(f"define void @{fname}() {{")
            self.emit("entry:")
            for s in stmt.statements:
                for l in self.lower_statement(s, parent_context=fname):
                    self.emit("  " + l)
            self.emit("  ret void")
            self.emit("}")
            self.emit("")  # blank line after function
        elif isinstance(stmt, nodes.Spawn):
            # create a stub function for spawn target (if possible) and call it
            # We generate a helper and call it directly (no threading). Real thread creation
            # should be mapped to runtime.spawn when integrating with a runtime.
            self.spawn_counter += 1
            fname = f"spawned_fn_{self.spawn_counter}"
            out.append(f"; spawn -> create/launch @{fname} (stubbed sequential call)")
            out.append(f"call void @{fname}()")
            # emit function body
            self.emit("")
            self.emit(f"define void @{fname}() {{")
            self.emit("entry:")
            # If spawn has an expression that is an identifier referring to a function, we would call it;
            # we don't have function values in this subset, so function is effectively empty.
            self.emit("  ; spawned function body (stub)")
            self.emit("  ret void")
            self.emit("}")
            self.emit("")
        elif isinstance(stmt, nodes.Lock):
            # call runtime helper with lock pointer as i8* (we represent lock as global by name)
            if isinstance(stmt.var, nodes.Identifier):
                lock_name = llvm_ident(stmt.var.name)
                out.append(f"; acquire lock @{lock_name}")
                out.append(f"call void @lock_acquire(i8* bitcast (i64* @{lock_name} to i8*))")
            else:
                out.append("; lock: unknown var")
        elif isinstance(stmt, nodes.Unlock):
            if isinstance(stmt.var, nodes.Identifier):
                lock_name = llvm_ident(stmt.var.name)
                out.append(f"; release lock @{lock_name}")
                out.append(f"call void @lock_release(i8* bitcast (i64* @{lock_name} to i8*))")
            else:
                out.append("; unlock: unknown var")
        elif isinstance(stmt, nodes.Atomic):
            out.append("; atomic enter")
            out.append("call void @atomic_enter()")
            for s in stmt.statements:
                for l in self.lower_statement(s, parent_context=parent_context):
                    out.append(l)
            out.append("; atomic exit")
            out.append("call void @atomic_exit()")
        else:
            out.append(f"; unhandled stmt type: {type(stmt).__name__}")
        return out

def generate_module(ast_root, output_path=None):
    """
    Generate a textual LLVM IR file (module.ll) for the given AST root.
    output_path: directory path where 'module.ll' will be written. Defaults to './test'.
    """
    if output_path is None:
        output_path = os.path.join(os.getcwd(), "test")
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    emitter = LLVMEmitter()
    if not isinstance(ast_root, nodes.Program):
        raise TypeError("generate_module expects ast_root of type nodes.Program")

    emitter.lower_program(ast_root)

    out_file = os.path.join(output_path, "module.ll")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(emitter.lines))
    print(f"LLVM IR written to {out_file}")
    return out_file

if __name__ == "__main__":
    # minimal smoke test: build a tiny AST and emit to ./test/module.ll
    p = nodes.Program([
        nodes.VarDecl("x", "int", init=nodes.Literal(0)),
        nodes.ChannelDecl("c", "int"),
        nodes.ParallelBlock([ nodes.Send(nodes.Identifier("c"), nodes.Literal(42)) ])
    ])
    generate_module(p)