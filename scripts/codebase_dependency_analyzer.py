#!/usr/bin/env python3
"""
Codebase Dependency Analyzer v1.1.0
Asynchronous Python 3.14-ready script for LLM-assisted development.

Outputs JSON only on stdout unless --output is used.
Progress and diagnostics go to stderr when --verbose is enabled.

For every analyzed Python file, output includes:
{
  "<relative/path/to/file.py>": {
    "consumed_by": ["<files that import this file>"],
    "consumes": ["<files this file imports>"],
    "missing_imported_symbols": [
      {
        "line": 123,
        "module": "pkg.module",
        "imported_name": "MissingName",
        "resolved_file": "<relative/pkg/module.py>"
      }
    ],
    "markdown_references": {
      "file_terms": ["<relative/path.py>", "<file.py>", "<file>"],
      "file_hits": [
        {
          "term": "<matched file term>",
          "markdown_file": "<relative/doc.md>",
          "line": 123,
          "snippet": "..."
        }
      ],
      "symbols": {
        "SymbolName": {
          "kinds": ["class" | "function" | "async_function"],
          "definitions": [
            {"line": 12, "kind": "class"}
          ],
          "hits": [
            {
              "term": "SymbolName",
              "markdown_file": "<relative/doc.md>",
              "line": 123,
              "snippet": "..."
            }
          ]
        }
      }
    }
  },
  ...
}

Usage:
  python codebase_dependency_analyzer.py /path/to/project
  python codebase_dependency_analyzer.py /path/to/project --path src/utils.py --output deps.json
  python codebase_dependency_analyzer.py . --path mypackage/ --exclude .git .venv node_modules
  python codebase_dependency_analyzer.py css/core/db/models
  python codebase_dependency_analyzer.py css/core/db/models --root .
  python codebase_dependency_analyzer.py . --no-markdown-refs

Pure stdlib • async I/O • zero external deps • Python 3.14 ready
"""

import argparse
import ast
import asyncio
import fnmatch
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Iterable, Literal, NamedTuple, TypeVar, TypedDict

SymbolKind = Literal["class", "function", "async_function"]
ImportKind = Literal["import", "from"]
MapResult = TypeVar("MapResult")


class MarkdownHit(TypedDict):
    term: str
    markdown_file: str
    line: int
    snippet: str


class SymbolDefinition(TypedDict):
    line: int
    kind: SymbolKind


class SymbolReference(TypedDict):
    kinds: list[SymbolKind]
    definitions: list[SymbolDefinition]
    hits: list[MarkdownHit]


class MarkdownReferences(TypedDict):
    file_terms: list[str]
    file_hits: list[MarkdownHit]
    symbols: dict[str, SymbolReference]


class DependencyGraphEntry(TypedDict):
    consumed_by: list[str]
    consumes: list[str]


class MissingImportedSymbol(TypedDict):
    line: int
    module: str
    imported_name: str
    resolved_file: str


class AnalyzerOutputEntry(DependencyGraphEntry, total=False):
    missing_imported_symbols: list[MissingImportedSymbol]
    markdown_references: MarkdownReferences


class SymbolDef(NamedTuple):
    name: str
    kind: SymbolKind
    line: int


class ImportRecord(NamedTuple):
    source_file: Path
    lineno: int
    kind: ImportKind
    module: str
    level: int
    imported_name: str | None = None


class ParsedPythonFile(NamedTuple):
    path: Path
    rel: str
    imports: tuple[ImportRecord, ...] = ()
    symbols: tuple[SymbolDef, ...] = ()
    exported_names: tuple[str, ...] = ()
    error: str | None = None


class MarkdownDoc(NamedTuple):
    path: Path
    rel: str
    lines: tuple[str, ...]
    error: str | None = None


class Diagnostic(NamedTuple):
    file: str
    message: str


def _rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _has_excluded_part(rel_path: Path, excludes: set[str]) -> bool:
    return any(part in excludes for part in rel_path.parts)


def _matches_any_glob(rel_posix: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(rel_posix, pattern) for pattern in patterns)


def _iter_project_files(
    root: Path,
    suffix: str,
    excludes: set[str],
    exclude_globs: list[str],
) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob(f"*{suffix}"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        rel_posix = rel.as_posix()
        if _has_excluded_part(rel, excludes):
            continue
        if _matches_any_glob(rel_posix, exclude_globs):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def _module_names_for_file(path: Path, root: Path, module_roots: list[Path]) -> set[str]:
    """Return every importable module alias for a Python file.

    Example for root/src/pkg/mod.py and module_roots=[root, root/src]:
      - src.pkg.mod
      - pkg.mod

    __init__.py maps to its package name.
    """
    names: set[str] = set()

    candidate_roots = [root, *module_roots]
    seen_roots: set[Path] = set()
    for base in candidate_roots:
        base = base.resolve(strict=False)
        if base in seen_roots:
            continue
        seen_roots.add(base)
        if not _is_within(path, base):
            continue
        rel = path.relative_to(base)
        if rel.name == "__init__.py":
            parts = rel.parts[:-1]
        else:
            parts = rel.with_suffix("").parts
        if parts:
            names.add(".".join(parts))

    return names


def _infer_module_roots(root: Path, explicit_roots: list[Path]) -> list[Path]:
    """Infer common import roots while staying stdlib-only.

    Explicit roots are resolved relative to the project root. The conventional
    src/ layout is included automatically if present.
    """
    roots: list[Path] = []

    src = root / "src"
    if src.is_dir():
        roots.append(src)

    for item in explicit_roots:
        candidate = item if item.is_absolute() else root / item
        candidate = candidate.resolve(strict=False)
        if candidate.is_dir() and _is_within(candidate, root):
            roots.append(candidate)

    # Stable de-duplication.
    deduped: list[Path] = []
    seen: set[Path] = set()
    for item in roots:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _build_module_index(
    root: Path,
    py_files: list[Path],
    module_roots: list[Path],
    include_namespace_packages: bool,
) -> dict[str, Path]:
    """Build dotted module name -> Python file index.

    Collision policy is deterministic: first file in sorted traversal wins.
    """
    module_index: dict[str, Path] = {}

    for file_path in py_files:
        for module_name in sorted(_module_names_for_file(file_path, root, module_roots)):
            module_index.setdefault(module_name, file_path)

    if include_namespace_packages:
        # Register package prefixes. If a real __init__.py exists, point to it.
        # Otherwise point to the first child module under that package. This lets
        # `from pkg import submodule` resolve pkg.submodule later, while avoiding
        # fake file nodes in final output.
        for module_name, file_path in list(module_index.items()):
            parts = module_name.split(".")
            for i in range(1, len(parts)):
                parent = ".".join(parts[:i])
                if parent in module_index:
                    continue
                init_candidate_paths = []
                for base in [root, *module_roots]:
                    init_candidate_paths.append(base / Path(*parts[:i]) / "__init__.py")
                init_path = next((p for p in init_candidate_paths if p.exists()), None)
                module_index[parent] = init_path or file_path

    return module_index


def _current_package_names(current_file: Path, root: Path, module_roots: list[Path]) -> list[str]:
    """Return possible package names for current_file, longest first."""
    names: list[str] = []
    for module_name in _module_names_for_file(current_file, root, module_roots):
        parts = module_name.split(".")
        if current_file.name == "__init__.py":
            package = module_name
        else:
            package = ".".join(parts[:-1])
        if package:
            names.append(package)
    return sorted(set(names), key=lambda n: (-n.count("."), n))


def _resolve_module_name(
    module_name: str,
    module_index: dict[str, Path],
) -> Path | None:
    """Resolve a dotted module name to a concrete Python file, if internal."""
    if not module_name:
        return None
    return module_index.get(module_name)


def _resolve_imported_module_candidate(
    module_name: str,
    imported_name: str | None,
    module_index: dict[str, Path],
) -> Path | None:
    """Resolve import target.

    For `from pkg import sub`, prefer pkg.sub if it is an internal module.
    Otherwise fall back to pkg itself if available.
    """
    if imported_name and imported_name != "*":
        child = f"{module_name}.{imported_name}" if module_name else imported_name
        resolved_child = _resolve_module_name(child, module_index)
        if resolved_child:
            return resolved_child

    return _resolve_module_name(module_name, module_index)


def _absolute_module_for_import_from(
    module: str,
    level: int,
    current_file: Path,
    root: Path,
    module_roots: list[Path],
) -> list[str]:
    """Convert ImportFrom.module + level into possible absolute module names.

    Python semantics:
      level=0: absolute import
      level=1: current package
      level=2: parent package
    """
    if level <= 0:
        return [module] if module else []

    candidates: list[str] = []
    for current_package in _current_package_names(current_file, root, module_roots):
        parts = current_package.split(".") if current_package else []
        pops = level - 1
        if pops > len(parts):
            continue
        base_parts = parts[: len(parts) - pops] if pops else parts
        if module:
            base_parts = [*base_parts, *module.split(".")]
        if base_parts:
            candidates.append(".".join(base_parts))

    return sorted(set(candidates), key=lambda n: (-n.count("."), n))


def _resolve_import_record(
    record: ImportRecord,
    root: Path,
    module_roots: list[Path],
    module_index: dict[str, Path],
) -> Path | None:
    if record.kind == "import":
        # `import a.b.c` binds `a`, but the dependency on a.b.c is useful if internal.
        # If a.b.c is not a file, progressively try parents.
        parts = record.module.split(".")
        for end in range(len(parts), 0, -1):
            candidate = ".".join(parts[:end])
            resolved = _resolve_module_name(candidate, module_index)
            if resolved:
                return resolved
        return None

    # ImportFrom.
    candidate_modules = _absolute_module_for_import_from(
        record.module,
        record.level,
        record.source_file,
        root,
        module_roots,
    )
    for module_name in candidate_modules:
        resolved = _resolve_imported_module_candidate(
            module_name,
            record.imported_name,
            module_index,
        )
        if resolved:
            return resolved
    return None


def _assigned_names(target: ast.expr) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        names: set[str] = set()
        for element in target.elts:
            names.update(_assigned_names(element))
        return names
    return set()


def _statement_bound_names(statements: list[ast.stmt]) -> set[str]:
    names: set[str] = set()
    for node in statements:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                names.update(_assigned_names(target))
        elif isinstance(node, ast.AnnAssign):
            names.update(_assigned_names(node.target))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".", maxsplit=1)[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    names.add(alias.asname or alias.name)
        elif isinstance(node, (ast.If, ast.While)):
            names.update(_statement_bound_names(node.body))
            names.update(_statement_bound_names(node.orelse))
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            names.update(_assigned_names(node.target))
            names.update(_statement_bound_names(node.body))
            names.update(_statement_bound_names(node.orelse))
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    names.update(_assigned_names(item.optional_vars))
            names.update(_statement_bound_names(node.body))
        elif isinstance(node, (ast.Try, ast.TryStar)):
            names.update(_statement_bound_names(node.body))
            names.update(_statement_bound_names(node.orelse))
            names.update(_statement_bound_names(node.finalbody))
            for handler in node.handlers:
                names.update(_statement_bound_names(handler.body))
        elif isinstance(node, ast.Match):
            for case in node.cases:
                names.update(_statement_bound_names(case.body))
    return names


def _top_level_bound_names(tree: ast.Module) -> tuple[str, ...]:
    return tuple(sorted(_statement_bound_names(tree.body)))


def _read_and_parse_python(path: Path, root: Path) -> ParsedPythonFile:
    rel = _rel_posix(path, root)
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content, filename=rel)
    except SyntaxError as exc:
        return ParsedPythonFile(path=path, rel=rel, error=f"SyntaxError: {exc.msg} at line {exc.lineno}")
    except (OSError, UnicodeError, ValueError) as exc:
        return ParsedPythonFile(path=path, rel=rel, error=f"{type(exc).__name__}: {exc}")

    imports: list[ImportRecord] = []
    symbols: list[SymbolDef] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    ImportRecord(
                        source_file=path,
                        lineno=getattr(node, "lineno", 0),
                        kind="import",
                        module=alias.name,
                        level=0,
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append(
                    ImportRecord(
                        source_file=path,
                        lineno=getattr(node, "lineno", 0),
                        kind="from",
                        module=node.module or "",
                        level=node.level or 0,
                        imported_name=alias.name,
                    )
                )
        elif isinstance(node, ast.ClassDef):
            symbols.append(SymbolDef(name=node.name, kind="class", line=node.lineno))
        elif isinstance(node, ast.AsyncFunctionDef):
            symbols.append(SymbolDef(name=node.name, kind="async_function", line=node.lineno))
        elif isinstance(node, ast.FunctionDef):
            symbols.append(SymbolDef(name=node.name, kind="function", line=node.lineno))

    symbols.sort(key=lambda s: (s.name, s.line, s.kind))
    return ParsedPythonFile(
        path=path,
        rel=rel,
        imports=tuple(imports),
        symbols=tuple(symbols),
        exported_names=_top_level_bound_names(tree),
    )


def _read_markdown(path: Path, root: Path) -> MarkdownDoc:
    rel = _rel_posix(path, root)
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return MarkdownDoc(path=path, rel=rel, lines=tuple(content.splitlines()))
    except (OSError, UnicodeError) as exc:
        return MarkdownDoc(path=path, rel=rel, lines=(), error=f"{type(exc).__name__}: {exc}")


async def _map_with_concurrency(
    items: list[Path],
    limit: int,
    func: Callable[[Path], MapResult],
) -> list[MapResult]:
    semaphore = asyncio.Semaphore(limit)

    async def run_one(item: Path) -> MapResult:
        async with semaphore:
            return await asyncio.to_thread(func, item)

    return await asyncio.gather(*(run_one(item) for item in items))


def _line_snippet(line: str, max_len: int) -> str:
    text = line.strip()
    if max_len <= 0 or len(text) <= max_len:
        return text
    if max_len <= 1:
        return text[:max_len]
    return text[: max_len - 1].rstrip() + "…"


def _compile_search_pattern(term: str, identifier: bool, case_insensitive: bool) -> re.Pattern[str]:
    flags = re.IGNORECASE if case_insensitive else 0
    escaped = re.escape(term)
    if identifier:
        return re.compile(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])", flags)
    return re.compile(escaped, flags)


def _find_markdown_hits(
    docs: list[MarkdownDoc],
    term: str,
    *,
    identifier: bool,
    case_insensitive: bool,
    max_hits: int,
    snippet_len: int,
) -> list[MarkdownHit]:
    if not term:
        return []

    pattern = _compile_search_pattern(term, identifier=identifier, case_insensitive=case_insensitive)
    hits: list[MarkdownHit] = []

    for doc in docs:
        if doc.error:
            continue
        for line_no, line in enumerate(doc.lines, start=1):
            if not pattern.search(line):
                continue
            hits.append(
                {
                    "term": term,
                    "markdown_file": doc.rel,
                    "line": line_no,
                    "snippet": _line_snippet(line, snippet_len),
                }
            )
            if max_hits > 0 and len(hits) >= max_hits:
                return hits

    return hits


def _file_reference_terms(rel: str) -> list[str]:
    path = Path(rel)
    terms = [rel, path.name, path.stem]
    # Stable de-duplication while preserving priority.
    deduped: list[str] = []
    seen: set[str] = set()
    for term in terms:
        if term and term not in seen:
            seen.add(term)
            deduped.append(term)
    return deduped


def _symbol_reference_index(symbols: Iterable[SymbolDef]) -> dict[str, SymbolReference]:
    indexed: dict[str, SymbolReference] = {}
    for symbol in symbols:
        if symbol.name not in indexed:
            indexed[symbol.name] = {
                "kinds": [],
                "definitions": [],
                "hits": [],
            }
        entry = indexed[symbol.name]
        if symbol.kind not in entry["kinds"]:
            entry["kinds"].append(symbol.kind)
        entry["definitions"].append({"line": symbol.line, "kind": symbol.kind})

    for entry in indexed.values():
        entry["kinds"].sort()
        entry["definitions"].sort(key=lambda item: (item["line"], item["kind"]))
    return dict(sorted(indexed.items(), key=lambda item: item[0]))


def _build_markdown_references(
    parsed: ParsedPythonFile,
    markdown_docs: list[MarkdownDoc],
    *,
    case_insensitive: bool,
    max_hits_per_term: int,
    snippet_len: int,
) -> MarkdownReferences:
    file_terms = _file_reference_terms(parsed.rel)
    file_hits: list[MarkdownHit] = []
    for term in file_terms:
        file_hits.extend(
            _find_markdown_hits(
                markdown_docs,
                term,
                identifier=False,
                case_insensitive=case_insensitive,
                max_hits=max_hits_per_term,
                snippet_len=snippet_len,
            )
        )

    # Deduplicate file hits because rel/path/name/stem may match the same line.
    seen_file_hits: set[tuple[str, int, str]] = set()
    deduped_file_hits: list[MarkdownHit] = []
    for hit in file_hits:
        key = (hit["markdown_file"], hit["line"], hit["snippet"])
        if key not in seen_file_hits:
            seen_file_hits.add(key)
            deduped_file_hits.append(hit)

    symbols = _symbol_reference_index(parsed.symbols)
    for symbol_name, entry in symbols.items():
        entry["hits"] = _find_markdown_hits(
            markdown_docs,
            symbol_name,
            identifier=True,
            case_insensitive=case_insensitive,
            max_hits=max_hits_per_term,
            snippet_len=snippet_len,
        )

    return {
        "file_terms": file_terms,
        "file_hits": sorted(deduped_file_hits, key=lambda h: (h["markdown_file"], h["line"], h["term"])),
        "symbols": symbols,
    }


def _select_output_files(all_files: list[Path], root: Path, target_path: Path | None) -> set[Path]:
    if target_path is None:
        return set(all_files)

    if target_path.is_file():
        return {target_path} if target_path.suffix == ".py" else set()

    return {path for path in all_files if _is_within(path, target_path)}


def _build_dependency_graph(
    root: Path,
    parsed_by_path: dict[Path, ParsedPythonFile],
    module_roots: list[Path],
    module_index: dict[str, Path],
) -> dict[str, DependencyGraphEntry]:
    graph: dict[str, DependencyGraphEntry] = {
        parsed.rel: {"consumed_by": [], "consumes": []}
        for parsed in sorted(parsed_by_path.values(), key=lambda p: p.rel)
    }

    for parsed in sorted(parsed_by_path.values(), key=lambda p: p.rel):
        consumes: set[str] = set()
        for record in parsed.imports:
            resolved = _resolve_import_record(record, root, module_roots, module_index)
            if not resolved:
                continue
            if resolved == parsed.path:
                continue
            if resolved not in parsed_by_path:
                # Could happen when a namespace package prefix points at a child file.
                continue
            consumes.add(_rel_posix(resolved, root))
        graph[parsed.rel]["consumes"] = sorted(consumes)

    for importer_rel, data in graph.items():
        for imported_rel in data["consumes"]:
            if imported_rel in graph:
                graph[imported_rel]["consumed_by"].append(importer_rel)

    for data in graph.values():
        data["consumed_by"] = sorted(set(data["consumed_by"]))
        data["consumes"] = sorted(set(data["consumes"]))

    return graph


def _find_missing_imported_symbols(
    parsed: ParsedPythonFile,
    root: Path,
    module_roots: list[Path],
    module_index: dict[str, Path],
    parsed_by_path: dict[Path, ParsedPythonFile],
) -> list[MissingImportedSymbol]:
    missing: list[MissingImportedSymbol] = []
    for record in parsed.imports:
        if record.kind != "from" or not record.imported_name or record.imported_name == "*":
            continue

        for module_name in _absolute_module_for_import_from(
            record.module,
            record.level,
            parsed.path,
            root,
            module_roots,
        ):
            imported_module = _resolve_module_name(f"{module_name}.{record.imported_name}", module_index)
            if imported_module is not None:
                break

            resolved_module = _resolve_module_name(module_name, module_index)
            if resolved_module is None:
                continue

            target = parsed_by_path.get(resolved_module)
            if target is not None and record.imported_name not in target.exported_names:
                missing.append(
                    {
                        "line": record.lineno,
                        "module": module_name,
                        "imported_name": record.imported_name,
                        "resolved_file": _rel_posix(resolved_module, root),
                    }
                )
            break

    return sorted(
        missing,
        key=lambda item: (item["line"], item["module"], item["imported_name"], item["resolved_file"]),
    )


async def analyze_codebase(
    root: Path,
    excludes: set[str],
    *,
    target_path: Path | None = None,
    exclude_globs: list[str] | None = None,
    explicit_module_roots: list[Path] | None = None,
    include_namespace_packages: bool = True,
    include_markdown_refs: bool = True,
    markdown_case_insensitive: bool = False,
    markdown_max_hits_per_term: int = 0,
    markdown_snippet_len: int = 180,
    concurrency: int = 64,
) -> tuple[dict[str, AnalyzerOutputEntry], list[Diagnostic]]:
    """Analyze codebase and return JSON-ready graph plus diagnostics.

    The full Python project is parsed even when target_path is provided. The final
    output is filtered to target_path. This keeps `consumed_by` globally correct.
    """
    diagnostics: list[Diagnostic] = []
    exclude_globs = exclude_globs or []
    explicit_module_roots = explicit_module_roots or []

    all_py_files = _iter_project_files(root, ".py", excludes, exclude_globs)
    output_files = _select_output_files(all_py_files, root, target_path)

    if target_path is not None and not output_files:
        return {}, diagnostics

    module_roots = _infer_module_roots(root, explicit_module_roots)
    module_index = _build_module_index(root, all_py_files, module_roots, include_namespace_packages)

    parsed_files_list = await _map_with_concurrency(
        all_py_files,
        max(1, concurrency),
        lambda p: _read_and_parse_python(p, root),
    )
    parsed_by_path: dict[Path, ParsedPythonFile] = {parsed.path: parsed for parsed in parsed_files_list}

    for parsed in parsed_files_list:
        if parsed.error:
            diagnostics.append(Diagnostic(file=parsed.rel, message=parsed.error))

    full_graph = _build_dependency_graph(root, parsed_by_path, module_roots, module_index)

    markdown_docs: list[MarkdownDoc] = []
    if include_markdown_refs:
        all_md_files = _iter_project_files(root, ".md", excludes, exclude_globs)
        markdown_docs = await _map_with_concurrency(
            all_md_files,
            max(1, concurrency),
            lambda p: _read_markdown(p, root),
        )
        for doc in markdown_docs:
            if doc.error:
                diagnostics.append(Diagnostic(file=doc.rel, message=doc.error))

    graph: dict[str, AnalyzerOutputEntry] = {}
    for path in sorted(output_files, key=lambda p: p.relative_to(root).as_posix()):
        parsed = parsed_by_path[path]
        entry: AnalyzerOutputEntry = {
            "consumed_by": full_graph[parsed.rel]["consumed_by"],
            "consumes": full_graph[parsed.rel]["consumes"],
            "missing_imported_symbols": _find_missing_imported_symbols(
                parsed,
                root,
                module_roots,
                module_index,
                parsed_by_path,
            ),
        }
        if include_markdown_refs:
            entry["markdown_references"] = _build_markdown_references(
                parsed,
                markdown_docs,
                case_insensitive=markdown_case_insensitive,
                max_hits_per_term=markdown_max_hits_per_term,
                snippet_len=markdown_snippet_len,
            )
        graph[parsed.rel] = entry

    return graph, diagnostics



PROJECT_ROOT_MARKERS = (
    ".git",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "tox.ini",
    "uv.lock",
    "poetry.lock",
    "pdm.lock",
)


def _has_project_root_marker(path: Path) -> bool:
    return any((path / marker).exists() for marker in PROJECT_ROOT_MARKERS)


def _find_project_root(start: Path) -> Path | None:
    """Find nearest project root marker at or above start."""
    cursor = start if start.is_dir() else start.parent
    cursor = cursor.resolve(strict=False)
    for candidate in (cursor, *cursor.parents):
        if _has_project_root_marker(candidate):
            return candidate
    return None


def _same_path(left: Path, right: Path) -> bool:
    return left.resolve(strict=False) == right.resolve(strict=False)


def _resolve_cli_scope(
    positional_path: Path,
    explicit_root: Path | None,
    explicit_focus: Path | None,
) -> tuple[Path, Path | None]:
    """Resolve CLI arguments into project root and optional focused target path.

    Backward compatible mode:
      analyzer.py /repo --path src/pkg

    Convenience mode for the common workflow:
      analyzer.py src/pkg

    In convenience mode, if src/pkg is below a detected project root, the full
    project is parsed and src/pkg is used only as the final output filter. This
    keeps consumed_by globally correct.
    """
    cwd = Path.cwd().resolve(strict=False)
    positional_resolved = (
        positional_path if positional_path.is_absolute() else cwd / positional_path
    ).resolve(strict=False)

    if explicit_root is not None:
        project_dir = (
            explicit_root if explicit_root.is_absolute() else cwd / explicit_root
        ).resolve(strict=False)
        if not project_dir.is_dir():
            raise ValueError(f"--root is not a directory: {project_dir}")
        if not _is_within(positional_resolved, project_dir):
            raise ValueError(f"path must stay inside --root: {positional_path}")

        target_path = None if _same_path(positional_resolved, project_dir) else positional_resolved
        if explicit_focus is not None:
            target_path = _resolve_target_path(project_dir, explicit_focus)
        return project_dir, target_path

    if explicit_focus is not None:
        # Original contract: positional argument is the project root.
        project_dir = positional_resolved
        if not project_dir.is_dir():
            raise ValueError(f"project_dir is not a directory: {project_dir}")
        return project_dir, _resolve_target_path(project_dir, explicit_focus)

    if not positional_resolved.exists():
        raise ValueError(f"path does not exist: {positional_resolved}")

    if positional_resolved.is_file():
        if positional_resolved.suffix != ".py":
            raise ValueError(f"file argument must be a .py file: {positional_resolved}")
        detected_root = _find_project_root(positional_resolved.parent)
        if detected_root and _is_within(positional_resolved, detected_root):
            return detected_root, positional_resolved
        return positional_resolved.parent, positional_resolved

    if not positional_resolved.is_dir():
        raise ValueError(f"path must be a directory or .py file: {positional_resolved}")

    # If the supplied directory itself looks like a project root, keep old behavior.
    if _has_project_root_marker(positional_resolved):
        return positional_resolved, None

    detected_root = _find_project_root(positional_resolved.parent)
    if detected_root and _is_within(positional_resolved, detected_root) and not _same_path(detected_root, positional_resolved):
        return detected_root, positional_resolved

    # Last fallback for marker-less projects: when a relative subtree is supplied
    # from a parent directory, use cwd as project root so external importers are
    # still visible. Absolute subtree paths keep the original behavior.
    if not positional_path.is_absolute() and _is_within(positional_resolved, cwd) and not _same_path(positional_resolved, cwd):
        return cwd, positional_resolved

    # Backward compatible fallback: treat positional path as the complete project.
    return positional_resolved, None


def _resolve_target_path(project_dir: Path, user_path: Path) -> Path:
    candidate = user_path if user_path.is_absolute() else project_dir / user_path
    target_path = candidate.resolve(strict=False)
    if not _is_within(target_path, project_dir):
        raise ValueError(f"--path must stay inside project_dir: {user_path}")
    return target_path


def _print_diagnostics(diagnostics: list[Diagnostic]) -> None:
    for diagnostic in diagnostics:
        print(f"WARNING: {diagnostic.file}: {diagnostic.message}", file=sys.stderr)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Async Python codebase dependency analyzer with Markdown reference scanning"
    )
    parser.add_argument(
        "path",
        type=Path,
        help=(
            "Project root, .py file, or focused subdirectory. "
            "If a focused path is below a detected project root, the full project is parsed."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Explicit project root. Useful when the positional path is a focused subdirectory.",
    )
    parser.add_argument(
        "--path",
        dest="path_filter",
        type=Path,
        default=None,
        help="Optional .py file or subdirectory to include in final output. Full project is still parsed.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON to this file instead of stdout",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[".git", "__pycache__", "venv", ".venv", "node_modules", "build", "dist", ".idea", ".vscode"],
        help="Directory/file path parts to skip",
    )
    parser.add_argument(
        "--exclude-glob",
        nargs="*",
        default=[],
        help="POSIX-style relative glob patterns to skip, e.g. '**/migrations/**' '*.generated.py'",
    )
    parser.add_argument(
        "--module-root",
        action="append",
        type=Path,
        default=[],
        help="Additional import root relative to project_dir. May be repeated. src/ is auto-detected.",
    )
    parser.add_argument(
        "--no-namespace-packages",
        action="store_true",
        help="Disable implicit namespace package prefix registration",
    )
    parser.add_argument(
        "--no-markdown-refs",
        action="store_true",
        help="Disable Markdown reference scanning",
    )
    parser.add_argument(
        "--markdown-case-insensitive",
        action="store_true",
        help="Search Markdown references case-insensitively",
    )
    parser.add_argument(
        "--markdown-max-hits-per-term",
        type=int,
        default=0,
        help="Maximum Markdown hits per searched term. 0 means unlimited.",
    )
    parser.add_argument(
        "--markdown-snippet-len",
        type=int,
        default=180,
        help="Maximum snippet length for Markdown hits. 0 means unlimited.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=64,
        help="Maximum concurrent file read/parse tasks",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress and diagnostics to stderr",
    )
    args = parser.parse_args()

    try:
        project_dir, target_path = _resolve_cli_scope(args.path, args.root, args.path_filter)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    if not project_dir.is_dir():
        print(f"ERROR: project root is not a directory: {project_dir}", file=sys.stderr)
        raise SystemExit(2)

    if target_path is not None:
        if target_path.is_file() and target_path.suffix != ".py":
            print(f"ERROR: focused file must be a .py file: {target_path}", file=sys.stderr)
            raise SystemExit(2)
        if not target_path.exists():
            print(f"ERROR: focused path does not exist: {target_path}", file=sys.stderr)
            raise SystemExit(2)
        if not (target_path.is_file() or target_path.is_dir()):
            print(f"ERROR: focused path must be a .py file or directory: {target_path}", file=sys.stderr)
            raise SystemExit(2)

    if args.concurrency < 1:
        print("ERROR: --concurrency must be >= 1", file=sys.stderr)
        raise SystemExit(2)

    if args.markdown_max_hits_per_term < 0:
        print("ERROR: --markdown-max-hits-per-term must be >= 0", file=sys.stderr)
        raise SystemExit(2)

    if args.verbose:
        scope = f" focused on {_rel_posix(target_path, project_dir)}" if target_path else ""
        print(f"Analyzing {project_dir}{scope}", file=sys.stderr)

    graph, diagnostics = await analyze_codebase(
        project_dir,
        set(args.exclude),
        target_path=target_path,
        exclude_globs=args.exclude_glob,
        explicit_module_roots=args.module_root,
        include_namespace_packages=not args.no_namespace_packages,
        include_markdown_refs=not args.no_markdown_refs,
        markdown_case_insensitive=args.markdown_case_insensitive,
        markdown_max_hits_per_term=args.markdown_max_hits_per_term,
        markdown_snippet_len=args.markdown_snippet_len,
        concurrency=args.concurrency,
    )

    if args.verbose and diagnostics:
        _print_diagnostics(diagnostics)

    output_json = json.dumps(graph, indent=2, sort_keys=True)

    if args.output:
        output_path = args.output if args.output.is_absolute() else Path.cwd() / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json + "\n", encoding="utf-8")
        if args.verbose:
            print(f"Wrote {len(graph)} file entries to {output_path}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    asyncio.run(main())
