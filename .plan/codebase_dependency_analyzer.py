#!/usr/bin/env python3
"""
Codebase Dependency Analyzer v0.9.1
Asynchronous Python 3.14 script for LLM-assisted development.

Outputs exactly:
{
  "<relative/path/to/file.py>": {
    "consumed_by": ["<list of files that import this one>"],
    "consumes": ["<list of files this one imports>"]
  },
  ...
}

Usage:
  python codebase_dependency_analyzer.py /path/to/project
  python codebase_dependency_analyzer.py /path/to/project --path src/utils.py --output deps.json
  python codebase_dependency_analyzer.py . --path mypackage/ --exclude venv .git

project_dir (required) + optional --path (file or subdir) for focused/smaller output.
Pure stdlib • async I/O • zero external deps • Python 3.14 ready
"""

import argparse
import ast
import asyncio
import json
from pathlib import Path


def _resolve_import(
    imported: str,
    level: int,
    current_file: Path,
    root: Path,
    module_index: dict,
) -> Path | None:
    """Resolve import string to actual .py file inside the project root."""
    if level > 0:
        # Relative import: from . import foo  or  from ..bar import baz
        rel = current_file.relative_to(root)
        package_parts = list(rel.parts[:-1])

        for _ in range(level):
            if package_parts:
                package_parts.pop()

        if imported:
            full = ".".join(package_parts + imported.split("."))
        else:
            full = ".".join(package_parts)
        return module_index.get(full)

    # Absolute import
    if imported in module_index:
        return module_index[imported]
    return None


async def analyze_codebase(
    root: Path, excludes: set, target_path: Path | None = None
) -> dict:
    """Core async analysis. Returns the exact dict requested.
    If target_path given, restricts which files are included in output,
    but module index is always built from the full project so imports resolve correctly.
    """
    # 1. Always build full module index from entire project (critical for correct "consumes")
    all_py_files: list[Path] = []
    for p in root.rglob("*.py"):
        if any(ex in p.parts for ex in excludes):
            continue
        all_py_files.append(p)

    module_index: dict[str, Path] = {}
    for f in all_py_files:
        rel = f.relative_to(root)
        if rel.name == "__init__.py":
            dotted = ".".join(rel.parts[:-1])
        else:
            dotted = ".".join(rel.with_suffix("").parts)
        module_index[dotted] = f

        # Support common src-layout: also register without leading "src."
        # e.g. "src.css.core.types" → also "css.core.types"
        if dotted.startswith("src."):
            stripped = dotted[4:]  # remove "src."
            if stripped and stripped not in module_index:
                module_index[stripped] = f

        # Register parent packages
        parts = dotted.split(".")
        for i in range(1, len(parts)):
            parent = ".".join(parts[:i])
            if parent not in module_index:
                init_path = root / Path(*parts[:i]) / "__init__.py"
                if init_path.exists():
                    module_index[parent] = init_path

                    # also register stripped parent if applicable
                    if parent.startswith("src."):
                        stripped_parent = parent[4:]
                        if stripped_parent and stripped_parent not in module_index:
                            module_index[stripped_parent] = init_path

    # 2. Decide which files to actually parse & include in output
    if target_path and target_path.is_file():
        py_files = [target_path] if target_path.suffix == ".py" else []
    elif target_path and target_path.is_dir():
        py_files = [p for p in all_py_files if p.is_relative_to(target_path)]
    else:
        py_files = all_py_files

    if not py_files:
        return {}

    # 3. Parse every file concurrently (I/O offloaded)
    async def parse_one(f: Path) -> tuple[str, list[str]]:
        rel_str = str(f.relative_to(root))
        try:
            content: str = await asyncio.to_thread(
                f.read_text, encoding="utf-8", errors="replace"
            )
            tree = ast.parse(content, filename=rel_str)

            consumes: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        resolved = _resolve_import(alias.name, 0, f, root, module_index)
                        if resolved:
                            consumes.append(str(resolved.relative_to(root)))
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    resolved_module = _resolve_import(mod, node.level or 0, f, root, module_index)
                    # Resolve each imported name relative to the resolved module
                    for alias in node.names:
                        if resolved_module:
                            # Try to resolve "module.name" (e.g. from . import foo → module=parent, name=foo)
                            resolved = _resolve_import(
                                f"{mod}.{alias.name}" if mod else alias.name,
                                node.level or 0,
                                f,
                                root,
                                module_index,
                            )
                            if resolved:
                                consumes.append(str(resolved.relative_to(root)))
                            elif resolved_module:
                                # Fallback: just record the module being imported from
                                consumes.append(str(resolved_module.relative_to(root)))
                        elif mod:
                            # Absolute import where module wasn't found in index
                            resolved = _resolve_import(alias.name, 0, f, root, module_index)
                            if resolved:
                                consumes.append(str(resolved.relative_to(root)))

            # deduplicate + sort for deterministic output
            consumes = sorted(set(consumes))
            return rel_str, consumes
        except SyntaxError:
            return rel_str, []
        except Exception:
            return rel_str, []

    parsed_results = await asyncio.gather(*[parse_one(f) for f in py_files])

    # 4. Build forward graph
    graph: dict[str, dict[str, list[str]]] = {}
    for path_str, consumes in parsed_results:
        graph[path_str] = {"consumed_by": [], "consumes": consumes}

    # 5. Reverse edges → consumed_by
    for path_str, data in graph.items():
        for consumed_path in data["consumes"]:
            if consumed_path in graph:
                if path_str not in graph[consumed_path]["consumed_by"]:
                    graph[consumed_path]["consumed_by"].append(path_str)

    # Final sort for cleanliness
    for data in graph.values():
        data["consumed_by"].sort()
        data["consumes"].sort()

    return graph


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Async Python 3.14 codebase dependency analyzer for LLM dev workflows"
    )
    parser.add_argument(
        "project_dir",
        type=Path,
        help="Root directory of the codebase (REQUIRED positional)",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Optional file or subdirectory to analyze only (reduces output size)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON to this file instead of stdout (default: stdout)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[".git", "__pycache__", "venv", ".venv", "node_modules", "build", "dist", ".idea", ".vscode"],
        help="Directory names to skip",
    )
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    if not project_dir.is_dir():
        print(f"ERROR: {project_dir} is not a directory")
        return

    excludes: set = set(args.exclude)
    print(f"Analyzing {project_dir} (Python 3.14 async)...", end="")

    # Handle optional --path (file or subdir) for focused analysis
    target_path: Path | None = None
    if args.path:
        candidate = args.path if args.path.is_absolute() else (project_dir / args.path)
        target_path = candidate.resolve(strict=False)
        if target_path.is_file() and target_path.suffix == ".py":
            print(f" (single file: {target_path.relative_to(project_dir)})")
        elif target_path.is_dir():
            print(f" (subtree: {target_path.relative_to(project_dir)}/)")
        else:
            exists_msg = "exists" if target_path.exists() else "does NOT exist"
            print(f"\nERROR: --path {args.path} resolved to {target_path}")
            print(f"       → {exists_msg} or is not a readable .py file / directory inside {project_dir}")
            print("       Tip: use full relative path from project root, e.g. src/core/types/")
            return
    else:
        print()

    graph = await analyze_codebase(project_dir, excludes, target_path)

    output_json = json.dumps(graph, indent=2, sort_keys=True)

    scope = f" ({len(graph)} files)"
    if target_path:
        scope = f" (focused on {target_path.relative_to(project_dir)}, {len(graph)} files)"

    if args.output:
        args.output.write_text(output_json, encoding="utf-8")
        print(f"Wrote dependency graph{scope} → {args.output}")
    else:
        print(output_json)
        print(f"\nDone{scope}.")


if __name__ == "__main__":
    asyncio.run(main())
