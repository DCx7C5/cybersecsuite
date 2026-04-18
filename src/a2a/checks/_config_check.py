"""Configuration consistency checks."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from a2a.checks._constants import _REPO_ROOT, _SRC_ROOT  # noqa: F401


def check_config() -> list[dict[str, str]]:
    """Verify config file consistency across mcp.json, docker-compose, settings.

    Checks:
      - ``mcp.json``: referenced Python files / modules exist on disk.
      - ``docker-compose.yml``: referenced Dockerfiles exist.
      - ``.claude/settings.json``: ASGI port numbers match docker-compose
        exposed ports.
      - ``pyproject.toml``: declared entry-point modules resolve.

    Returns:
        List of finding dicts with keys ``level``, ``check``, and ``message``.
    """
    findings: list[dict[str, str]] = []
    _check_mcp_json(findings)
    _check_docker_compose(findings)
    _check_settings_ports(findings)
    _check_pyproject_entrypoints(findings)
    return findings


# ═══════════════════════════════════════════════════════════════════════════
# run_all_checks
# ═══════════════════════════════════════════════════════════════════════════

# ── Config sub-checks ─────────────────────────────────────────────────────


def _check_mcp_json(findings: list[dict[str, str]]) -> None:
    """Verify mcp.json server command paths exist on disk."""
    mcp_path = _REPO_ROOT / "mcp.json"
    if not mcp_path.exists():
        findings.append(
            {
                "level": "error",
                "check": "config",
                "message": "mcp.json not found at repository root",
            }
        )
        return

    try:
        data = json.loads(mcp_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        findings.append(
            {
                "level": "error",
                "check": "config",
                "message": f"Cannot parse mcp.json: {exc}",
            }
        )
        return

    servers = data.get("mcpServers", {})
    before = len(findings)
    for name, cfg in servers.items():
        args: list[str] = cfg.get("args", [])
        # Resolve ${workspaceFolder} → repo root.
        resolved = [a.replace("${workspaceFolder}", str(_REPO_ROOT)) for a in args]

        # Check --directory paths.
        for i, arg in enumerate(resolved):
            if arg == "--directory" and i + 1 < len(resolved):
                dir_path = Path(resolved[i + 1])
                if not dir_path.is_dir():
                    findings.append(
                        {
                            "level": "error",
                            "check": "config",
                            "message": (
                                f"mcp.json server '{name}': --directory path "
                                f"'{resolved[i + 1]}' does not exist"
                            ),
                        }
                    )

        # Check if referenced Python files exist.
        for arg in resolved:
            if arg.endswith(".py") and not arg.startswith("-"):
                py_path = Path(arg)
                if not py_path.is_absolute():
                    # Relative to the --directory or repo root.
                    dir_idx = None
                    for j, a in enumerate(resolved):
                        if a == "--directory" and j + 1 < len(resolved):
                            dir_idx = j + 1
                            break
                    base = Path(resolved[dir_idx]) if dir_idx is not None else _REPO_ROOT
                    py_path = base / arg
                if not py_path.exists():
                    findings.append(
                        {
                            "level": "warning",
                            "check": "config",
                            "message": (
                                f"mcp.json server '{name}': Python file '{arg}' not found on disk"
                            ),
                        }
                    )

    if len(findings) == before:
        findings.append(
            {"level": "info", "check": "config", "message": f"mcp.json: {len(servers)} server(s) validated OK"}
        )


def _check_docker_compose(findings: list[dict[str, str]]) -> None:
    """Verify Dockerfiles referenced in docker-compose.yml exist."""
    dc_path = _REPO_ROOT / "docker-compose.yml"
    if not dc_path.exists():
        findings.append(
            {
                "level": "warning",
                "check": "config",
                "message": "docker-compose.yml not found at repository root",
            }
        )
        return

    content = dc_path.read_text()

    # Extract build context + dockerfile pairs via regex (avoids pyyaml for
    # x-anchors which stdlib yaml doesn't handle).
    # Pattern: context: <path> ... dockerfile: <path>
    build_blocks = re.findall(
        r"build:\s*\n\s+context:\s*(.+?)\s*\n\s+dockerfile:\s*(.+)",
        content,
    )

    before = len(findings)
    for context, dockerfile in build_blocks:
        context = context.strip()
        dockerfile = dockerfile.strip()
        if context == ".":
            full_path = _REPO_ROOT / dockerfile
        else:
            full_path = _REPO_ROOT / context / dockerfile
        if not full_path.exists():
            findings.append(
                {
                    "level": "error",
                    "check": "config",
                    "message": (
                        f"docker-compose.yml: Dockerfile not found: "
                        f"{full_path.relative_to(_REPO_ROOT)}"
                    ),
                }
            )

    if len(findings) == before:
        findings.append(
            {"level": "info", "check": "config", "message": "docker-compose.yml: Dockerfiles validated OK"}
        )


def _check_settings_ports(findings: list[dict[str, str]]) -> None:
    """Verify .claude/settings.json ports match docker-compose exposed ports."""
    settings_path = _REPO_ROOT / ".claude" / "settings.json"
    dc_path = _REPO_ROOT / "docker-compose.yml"

    if not settings_path.exists() or not dc_path.exists():
        return

    try:
        settings = json.loads(settings_path.read_text())
    except (json.JSONDecodeError, OSError):
        findings.append(
            {
                "level": "warning",
                "check": "config",
                "message": "Cannot parse .claude/settings.json",
            }
        )
        return

    # Extract ASGI ports from settings.
    asgi = settings.get("asgi", {})
    settings_ports: set[int] = set()
    for key in ("port", "alt_port", "tls_port"):
        val = asgi.get(key)
        if isinstance(val, int):
            settings_ports.add(val)

    if not settings_ports:
        return

    # Extract exposed ports from docker-compose.
    dc_content = dc_path.read_text()
    dc_ports: set[int] = set()
    for match in re.finditer(r'"[\d.]+:(\d+):\d+"', dc_content):
        dc_ports.add(int(match.group(1)))

    missing = settings_ports - dc_ports
    for port in sorted(missing):
        findings.append(
            {
                "level": "warning",
                "check": "config",
                "message": (
                    f".claude/settings.json declares ASGI port {port} "
                    f"but it is not exposed in docker-compose.yml"
                ),
            }
        )


def _check_pyproject_entrypoints(findings: list[dict[str, str]]) -> None:
    """Verify pyproject.toml entry-point modules resolve to files in src/."""
    pyproject_path = _REPO_ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        findings.append(
            {
                "level": "warning",
                "check": "config",
                "message": "pyproject.toml not found at repository root",
            }
        )
        return

    content = pyproject_path.read_text()

    # Parse [project.scripts] entries: name = "module:func"
    in_scripts = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[project.scripts]":
            in_scripts = True
            continue
        if in_scripts:
            if stripped.startswith("["):
                break  # new section
            match = re.match(r'(\S+)\s*=\s*"([^"]+)"', stripped)
            if not match:
                continue
            ep_name, ep_ref = match.group(1), match.group(2)
            # ep_ref is "module.path:function"
            if ":" not in ep_ref:
                continue
            module_part, func_name = ep_ref.rsplit(":", 1)
            module_path = _SRC_ROOT / module_part.replace(".", "/")

            # Could be a package (__init__.py) or a file (.py).
            candidates = [
                module_path.with_suffix(".py"),
                module_path / "__init__.py",
            ]
            if not any(c.exists() for c in candidates):
                findings.append(
                    {
                        "level": "error",
                        "check": "config",
                        "message": (
                            f"pyproject.toml entry point '{ep_name}' references "
                            f"module '{module_part}' which cannot be found in src/"
                        ),
                    }
                )
                continue

            # Verify the function exists in the module.
            resolved_file = next(c for c in candidates if c.exists())
            try:
                tree = ast.parse(resolved_file.read_text())
            except SyntaxError:
                continue
            func_names = {
                n.name
                for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            if func_name not in func_names:
                findings.append(
                    {
                        "level": "error",
                        "check": "config",
                        "message": (
                            f"pyproject.toml entry point '{ep_name}': function "
                            f"'{func_name}' not found in {resolved_file.name}"
                        ),
                    }
                )
