from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


ARCHIVE_FRAGMENT = "reports/archive"
ALLOWED_ARCHIVE_WRITERS = {
    "src/subsystem_emergence/reports/archive/cross_domain.py",
    "src/subsystem_emergence/reports/archive/paper_e.py",
}
WRITE_METHODS = {"mkdir", "open", "touch", "unlink", "write", "write_bytes", "write_text"}
PATH_ARG_WRITE_CALLS = {"copy2", "copytree", "replace", "rename", "savefig"}
PATH_PASSTHROUGH_METHODS = {"absolute", "as_posix", "resolve"}
SKIPPED_SCAN_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "tmp",
    "venv",
}
TEXTUAL_WRITE_TOKENS = {
    ".mkdir(": "mkdir",
    ".write(": "write",
    ".write_bytes(": "write_bytes",
    ".write_text(": "write_text",
    ".unlink(": "unlink",
    ".touch(": "touch",
    "copy2(": "copy2",
    "copytree(": "copytree",
    "open(": "open",
    "savefig(": "savefig",
}


@dataclass(frozen=True)
class ArchiveWriteOccurrence:
    source_path: Path
    lineno: int
    kind: str
    detail: str

    def relative_source(self, scan_root: Path) -> str:
        return self.source_path.relative_to(scan_root).as_posix()


class _FunctionSinkAnalyzer:
    def __init__(self, parameters: list[str], known_sink_helpers: set[str]) -> None:
        self._known_sink_helpers = known_sink_helpers
        self._scopes: list[dict[str, bool]] = [{parameter: True for parameter in parameters}]
        self.sink_like = False

    def analyze(self, statements: list[ast.stmt]) -> bool:
        self._analyze_block(statements)
        return self.sink_like

    def _analyze_block(self, statements: list[ast.stmt]) -> None:
        for statement in statements:
            self._analyze_statement(statement)

    def _analyze_statement(self, statement: ast.stmt) -> None:
        if isinstance(statement, ast.Assign):
            self._inspect_expr(statement.value)
            tainted = self._expr_tainted(statement.value)
            for target in statement.targets:
                self._bind_target(target, tainted)
            return

        if isinstance(statement, ast.AnnAssign):
            if statement.value is not None:
                self._inspect_expr(statement.value)
            self._bind_target(statement.target, self._expr_tainted(statement.value))
            return

        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return

        if isinstance(statement, ast.With):
            for item in statement.items:
                self._inspect_expr(item.context_expr)
                if item.optional_vars is not None:
                    self._bind_target(item.optional_vars, self._expr_tainted(item.context_expr))
            self._push_scope()
            self._analyze_block(statement.body)
            self._pop_scope()
            return

        if isinstance(statement, ast.If):
            self._inspect_expr(statement.test)
            self._push_scope()
            self._analyze_block(statement.body)
            self._pop_scope()
            self._push_scope()
            self._analyze_block(statement.orelse)
            self._pop_scope()
            return

        if isinstance(statement, (ast.For, ast.AsyncFor)):
            self._inspect_expr(statement.iter)
            self._push_scope()
            self._bind_target(statement.target, False)
            self._analyze_block(statement.body)
            self._analyze_block(statement.orelse)
            self._pop_scope()
            return

        if isinstance(statement, ast.Try):
            self._push_scope()
            self._analyze_block(statement.body)
            self._pop_scope()
            for handler in statement.handlers:
                self._push_scope()
                if handler.name:
                    self._current_scope()[handler.name] = False
                self._analyze_block(handler.body)
                self._pop_scope()
            self._push_scope()
            self._analyze_block(statement.orelse)
            self._pop_scope()
            self._push_scope()
            self._analyze_block(statement.finalbody)
            self._pop_scope()
            return

        if isinstance(statement, ast.Expr):
            self._inspect_expr(statement.value)
            return

        if isinstance(statement, ast.Return) and statement.value is not None:
            self._inspect_expr(statement.value)
            return

        for child in ast.iter_child_nodes(statement):
            if isinstance(child, ast.expr):
                self._inspect_expr(child)

    def _inspect_expr(self, expression: ast.expr | None) -> None:
        if expression is None or self.sink_like:
            return
        if isinstance(expression, ast.Call):
            if self._call_uses_tainted_sink(expression):
                self.sink_like = True
                return
            self._inspect_expr(expression.func)
            for argument in expression.args:
                self._inspect_expr(argument)
            for keyword in expression.keywords:
                self._inspect_expr(keyword.value)
            return
        if isinstance(expression, ast.BinOp):
            self._inspect_expr(expression.left)
            self._inspect_expr(expression.right)
            return
        if isinstance(expression, ast.Attribute):
            self._inspect_expr(expression.value)
            return
        if isinstance(expression, ast.Subscript):
            self._inspect_expr(expression.value)
            self._inspect_expr(expression.slice)
            return
        if isinstance(expression, ast.Dict):
            for key in expression.keys:
                self._inspect_expr(key)
            for value in expression.values:
                self._inspect_expr(value)
            return
        if isinstance(expression, (ast.List, ast.Set, ast.Tuple)):
            for element in expression.elts:
                self._inspect_expr(element)
            return
        if isinstance(expression, ast.JoinedStr):
            for value in expression.values:
                if isinstance(value, ast.FormattedValue):
                    self._inspect_expr(value.value)

    def _call_uses_tainted_sink(self, call: ast.Call) -> bool:
        if isinstance(call.func, ast.Attribute):
            method = call.func.attr
            if method in WRITE_METHODS:
                return self._expr_tainted(call.func.value)
            if method in PATH_ARG_WRITE_CALLS and call.args:
                return self._expr_tainted(call.args[0])
            return False

        if isinstance(call.func, ast.Name):
            if call.func.id == "open" and call.args:
                return self._expr_tainted(call.args[0])
            if call.func.id in self._known_sink_helpers:
                return any(self._expr_tainted(argument) for argument in call.args) or any(
                    self._expr_tainted(keyword.value) for keyword in call.keywords
                )
        return False

    def _expr_tainted(self, expression: ast.AST | None) -> bool:
        if expression is None:
            return False
        if isinstance(expression, ast.Name):
            return self._lookup(expression.id)
        if isinstance(expression, ast.Attribute):
            return self._expr_tainted(expression.value)
        if isinstance(expression, ast.Subscript):
            return self._expr_tainted(expression.value) or self._expr_tainted(expression.slice)
        if isinstance(expression, ast.BinOp):
            return self._expr_tainted(expression.left) or self._expr_tainted(expression.right)
        if isinstance(expression, ast.Call):
            if isinstance(expression.func, ast.Name) and expression.func.id == "Path":
                return any(self._expr_tainted(argument) for argument in expression.args)
            if isinstance(expression.func, ast.Attribute) and expression.func.attr in PATH_PASSTHROUGH_METHODS:
                return self._expr_tainted(expression.func.value)
            return any(self._expr_tainted(argument) for argument in expression.args) or any(
                self._expr_tainted(keyword.value) for keyword in expression.keywords
            )
        if isinstance(expression, ast.JoinedStr):
            return any(
                self._expr_tainted(value.value)
                for value in expression.values
                if isinstance(value, ast.FormattedValue)
            )
        if isinstance(expression, ast.Dict):
            return any(self._expr_tainted(key) for key in expression.keys) or any(
                self._expr_tainted(value) for value in expression.values
            )
        if isinstance(expression, (ast.List, ast.Set, ast.Tuple)):
            return any(self._expr_tainted(element) for element in expression.elts)
        return False

    def _bind_target(self, target: ast.expr, tainted: bool) -> None:
        if isinstance(target, ast.Name):
            self._current_scope()[target.id] = tainted
            return
        if isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                self._bind_target(element, tainted)

    def _lookup(self, name: str) -> bool:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return False

    def _push_scope(self) -> None:
        self._scopes.append(dict(self._current_scope()))

    def _pop_scope(self) -> None:
        self._scopes.pop()

    def _current_scope(self) -> dict[str, bool]:
        return self._scopes[-1]


class _ArchiveWriteAnalyzer:
    def __init__(self, source_path: Path, sink_helpers: set[str]) -> None:
        self.source_path = source_path
        self._sink_helpers = sink_helpers
        self.occurrences: list[ArchiveWriteOccurrence] = []
        self._scopes: list[dict[str, str | None]] = [{}]

    def analyze(self, tree: ast.AST) -> list[ArchiveWriteOccurrence]:
        self._analyze_block(getattr(tree, "body", []))
        return self.occurrences

    def _analyze_block(self, statements: list[ast.stmt]) -> None:
        for statement in statements:
            self._analyze_statement(statement)

    def _analyze_statement(self, statement: ast.stmt) -> None:
        if isinstance(statement, ast.Assign):
            self._inspect_expr(statement.value)
            value = self._static_path(statement.value)
            for target in statement.targets:
                self._bind_target(target, value)
            return

        if isinstance(statement, ast.AnnAssign):
            if statement.value is not None:
                self._inspect_expr(statement.value)
            self._bind_target(statement.target, self._static_path(statement.value))
            return

        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._push_scope()
            for argument in statement.args.posonlyargs + statement.args.args + statement.args.kwonlyargs:
                self._current_scope()[argument.arg] = None
            if statement.args.vararg is not None:
                self._current_scope()[statement.args.vararg.arg] = None
            if statement.args.kwarg is not None:
                self._current_scope()[statement.args.kwarg.arg] = None
            self._analyze_block(statement.body)
            self._pop_scope()
            return

        if isinstance(statement, ast.With):
            for item in statement.items:
                self._inspect_expr(item.context_expr)
                if item.optional_vars is not None:
                    self._bind_target(item.optional_vars, self._static_path(item.context_expr))
            self._push_scope()
            self._analyze_block(statement.body)
            self._pop_scope()
            return

        if isinstance(statement, ast.If):
            self._inspect_expr(statement.test)
            self._push_scope()
            self._analyze_block(statement.body)
            self._pop_scope()
            self._push_scope()
            self._analyze_block(statement.orelse)
            self._pop_scope()
            return

        if isinstance(statement, (ast.For, ast.AsyncFor)):
            self._inspect_expr(statement.iter)
            self._push_scope()
            self._bind_target(statement.target, None)
            self._analyze_block(statement.body)
            self._analyze_block(statement.orelse)
            self._pop_scope()
            return

        if isinstance(statement, ast.Try):
            self._push_scope()
            self._analyze_block(statement.body)
            self._pop_scope()
            for handler in statement.handlers:
                self._push_scope()
                if handler.name:
                    self._current_scope()[handler.name] = None
                self._analyze_block(handler.body)
                self._pop_scope()
            self._push_scope()
            self._analyze_block(statement.orelse)
            self._pop_scope()
            self._push_scope()
            self._analyze_block(statement.finalbody)
            self._pop_scope()
            return

        if isinstance(statement, ast.Expr):
            self._inspect_expr(statement.value)
            return

        if isinstance(statement, ast.Return) and statement.value is not None:
            self._inspect_expr(statement.value)
            return

        for child in ast.iter_child_nodes(statement):
            if isinstance(child, ast.expr):
                self._inspect_expr(child)

    def _inspect_expr(self, expression: ast.expr | None) -> None:
        if expression is None:
            return
        if isinstance(expression, ast.Call):
            self._record_call(expression)
            self._inspect_expr(expression.func)
            for argument in expression.args:
                self._inspect_expr(argument)
            for keyword in expression.keywords:
                self._inspect_expr(keyword.value)
            return
        if isinstance(expression, ast.BinOp):
            self._inspect_expr(expression.left)
            self._inspect_expr(expression.right)
            return
        if isinstance(expression, ast.Attribute):
            self._inspect_expr(expression.value)
            return
        if isinstance(expression, ast.Subscript):
            self._inspect_expr(expression.value)
            self._inspect_expr(expression.slice)
            return
        if isinstance(expression, ast.Dict):
            for key in expression.keys:
                self._inspect_expr(key)
            for value in expression.values:
                self._inspect_expr(value)
            return
        if isinstance(expression, (ast.List, ast.Set, ast.Tuple)):
            for element in expression.elts:
                self._inspect_expr(element)
            return
        if isinstance(expression, ast.JoinedStr):
            for value in expression.values:
                if isinstance(value, ast.FormattedValue):
                    self._inspect_expr(value.value)

    def _record_call(self, call: ast.Call) -> None:
        if isinstance(call.func, ast.Attribute):
            method = call.func.attr
            receiver_path = self._static_path(call.func.value)
            if method in WRITE_METHODS and self._is_archive_path(receiver_path):
                self._add_occurrence(call, method, receiver_path)
            elif method in PATH_ARG_WRITE_CALLS and call.args:
                target_path = self._static_path(call.args[0])
                if self._is_archive_path(target_path):
                    self._add_occurrence(call, method, target_path)
            return

        if not isinstance(call.func, ast.Name):
            return

        target_path = next(
            (
                candidate
                for candidate in [self._static_path(argument) for argument in call.args]
                + [self._static_path(keyword.value) for keyword in call.keywords]
                if self._is_archive_path(candidate)
            ),
            None,
        )
        if call.func.id == "open" and target_path is not None:
            self._add_occurrence(call, "open", target_path)
        elif call.func.id in self._sink_helpers and target_path is not None:
            self._add_occurrence(call, call.func.id, target_path)

    def _add_occurrence(self, call: ast.Call, kind: str, detail: str | None) -> None:
        self.occurrences.append(
            ArchiveWriteOccurrence(
                source_path=self.source_path,
                lineno=call.lineno,
                kind=kind,
                detail=detail or ARCHIVE_FRAGMENT,
            )
        )

    def _bind_target(self, target: ast.expr, value: str | None) -> None:
        if isinstance(target, ast.Name):
            self._current_scope()[target.id] = value
            return
        if isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                self._bind_target(element, value)

    def _static_path(self, node: ast.AST | None) -> str | None:
        if node is None:
            return None

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return self._normalize(node.value)

        if isinstance(node, ast.JoinedStr):
            parts: list[str] = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    parts.append(value.value)
                else:
                    return self._normalize("".join(parts)) if parts else None
            return self._normalize("".join(parts))

        if isinstance(node, ast.Name):
            return self._lookup(node.id)

        if isinstance(node, ast.Attribute):
            if node.attr == "parent":
                return self._static_path(node.value)
            return None

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return self._join_fragments(self._static_path(node.left), self._static_path(node.right))

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "Path" and node.args:
                return self._static_path(node.args[0])
            if isinstance(node.func, ast.Attribute) and node.func.attr in PATH_PASSTHROUGH_METHODS:
                return self._static_path(node.func.value)
            fragments = [self._static_path(argument) for argument in call_path_arguments(node)]
            archive_fragments = [fragment for fragment in fragments if self._is_archive_path(fragment)]
            if archive_fragments:
                return archive_fragments[0]
            return None

        return None

    @staticmethod
    def _join_fragments(left: str | None, right: str | None) -> str | None:
        if left is None and right is None:
            return None
        if left is None:
            return _ArchiveWriteAnalyzer._normalize(right)
        if right is None:
            return _ArchiveWriteAnalyzer._normalize(left)
        return _ArchiveWriteAnalyzer._normalize(f"{left.rstrip('/')}/{right.lstrip('/')}")

    @staticmethod
    def _normalize(value: str | None) -> str | None:
        if value is None:
            return None
        return str(value).replace("\\", "/")

    @staticmethod
    def _is_archive_path(value: str | None) -> bool:
        return value is not None and ARCHIVE_FRAGMENT in value

    def _lookup(self, name: str) -> str | None:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def _push_scope(self) -> None:
        self._scopes.append(dict(self._current_scope()))

    def _pop_scope(self) -> None:
        self._scopes.pop()

    def _current_scope(self) -> dict[str, str | None]:
        return self._scopes[-1]


def call_path_arguments(node: ast.Call) -> list[ast.expr]:
    return list(node.args) + [keyword.value for keyword in node.keywords]


def iter_python_sources(scan_root: Path) -> list[Path]:
    return [
        source_path
        for source_path in sorted(scan_root.rglob("*.py"))
        if not any(part in SKIPPED_SCAN_DIRS for part in source_path.relative_to(scan_root).parts)
        and "tests" not in source_path.relative_to(scan_root).parts
    ]


def parse_python_sources(scan_root: Path) -> dict[Path, ast.AST]:
    parsed: dict[Path, ast.AST] = {}
    for source_path in iter_python_sources(scan_root):
        try:
            parsed[source_path] = ast.parse(source_path.read_text(), filename=str(source_path))
        except SyntaxError:
            continue
    return parsed


def discover_sink_helpers(parsed_sources: dict[Path, ast.AST]) -> set[str]:
    sink_helpers: set[str] = set()
    changed = True
    while changed:
        changed = False
        for tree in parsed_sources.values():
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                parameter_names = [argument.arg for argument in node.args.posonlyargs + node.args.args + node.args.kwonlyargs]
                if node.args.vararg is not None:
                    parameter_names.append(node.args.vararg.arg)
                if node.args.kwarg is not None:
                    parameter_names.append(node.args.kwarg.arg)
                if _FunctionSinkAnalyzer(parameter_names, sink_helpers).analyze(node.body) and node.name not in sink_helpers:
                    sink_helpers.add(node.name)
                    changed = True
    return sink_helpers


def collect_textual_archive_writes(scan_root: Path, parsed_sources: dict[Path, ast.AST]) -> list[ArchiveWriteOccurrence]:
    parsed_paths = set(parsed_sources)
    occurrences: list[ArchiveWriteOccurrence] = []
    for source_path in iter_python_sources(scan_root):
        if source_path in parsed_paths:
            continue
        lines = source_path.read_text().splitlines()
        for lineno, line in enumerate(lines, start=1):
            normalized = line.replace("\\", "/")
            if ARCHIVE_FRAGMENT not in normalized:
                continue
            for token, kind in TEXTUAL_WRITE_TOKENS.items():
                if token in normalized:
                    occurrences.append(
                        ArchiveWriteOccurrence(
                            source_path=source_path,
                            lineno=lineno,
                            kind=kind,
                            detail=ARCHIVE_FRAGMENT,
                        )
                    )
    return occurrences


def collect_archive_write_occurrences(scan_root: Path) -> list[ArchiveWriteOccurrence]:
    parsed_sources = parse_python_sources(scan_root)
    sink_helpers = discover_sink_helpers(parsed_sources)
    occurrences: list[ArchiveWriteOccurrence] = []
    for source_path, tree in parsed_sources.items():
        occurrences.extend(_ArchiveWriteAnalyzer(source_path, sink_helpers).analyze(tree))
    occurrences.extend(collect_textual_archive_writes(scan_root, parsed_sources))
    return occurrences


def collect_unauthorized_archive_writes(scan_root: Path) -> list[ArchiveWriteOccurrence]:
    return [
        occurrence
        for occurrence in collect_archive_write_occurrences(scan_root)
        if occurrence.relative_source(scan_root) not in ALLOWED_ARCHIVE_WRITERS
    ]


def _format_occurrences(scan_root: Path, occurrences: list[ArchiveWriteOccurrence]) -> str:
    return "\n".join(
        f"{occurrence.relative_source(scan_root)}:{occurrence.lineno} {occurrence.kind} -> {occurrence.detail}"
        for occurrence in occurrences
    )


def test_only_archive_generators_can_write_archive_outputs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    violations = collect_unauthorized_archive_writes(repo_root)

    assert not violations, (
        "Unauthorized reports/archive write behavior detected outside the archive generators:\n"
        f"{_format_occurrences(repo_root, violations)}"
    )
