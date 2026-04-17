"""
Specialized developer agents — Python Developer, C++ Developer, etc.
Each exposes an AgentCard and executes language-specific tasks.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from a2a.registry import AgentRegistry

from a2a.agent import BaseA2AAgent
from a2a.enums import AuthScheme, PartType
from a2a.models import (
    AgentCard, AgentCapabilities, AgentAuthentication, AgentSkill,
    Task, Message, TextPart, TaskArtifact,
)
from a2a.task_store import TaskStore


# ─── Python Developer Agent ───────────────────────────────────────────────────

def build_python_agent_card(base_url: str = "http://localhost:8001") -> AgentCard:
    return AgentCard(
        name="PythonDeveloper",
        description="Expert Python developer — writes, reviews, and debugs Python code.",
        url=base_url,
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True),
        authentication=AgentAuthentication(schemes=[AuthScheme.ED25519]),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="python-write",
                name="Write Python",
                description="Write Python scripts, modules, and packages.",
                tags=["python", "code", "write", "script", "develop"],
                examples=["Write a Python CVE parser", "Implement a BLAKE2b hasher in Python"],
            ),
            AgentSkill(
                id="python-review",
                name="Review Python",
                description="Review Python code for bugs, security, and style.",
                tags=["python", "review", "audit", "security"],
                examples=["Review this Python code for security issues"],
            ),
            AgentSkill(
                id="python-debug",
                name="Debug Python",
                description="Debug Python errors and stack traces.",
                tags=["python", "debug", "error", "fix"],
                examples=["Debug this Python traceback"],
            ),
            AgentSkill(
                id="python-test",
                name="Write Python Tests",
                description="Write pytest test suites for Python code.",
                tags=["python", "test", "pytest", "coverage"],
                examples=["Write tests for this function"],
            ),
        ],
        provider={"name": "cybersecsuite", "url": base_url},
    )


class PythonDeveloperAgent(BaseA2AAgent):
    """Specialized agent for Python development tasks."""

    SKILL_KEYWORDS = {
        "python-write":  ("write", "create", "implement", "build", "generate", "script"),
        "python-review": ("review", "audit", "check", "analyse", "analyze"),
        "python-debug":  ("debug", "fix", "error", "traceback", "exception", "crash"),
        "python-test":   ("test", "pytest", "spec", "coverage", "unit"),
    }

    def __init__(self, base_url: str = "http://localhost:8001", store: Optional[TaskStore] = None) -> None:
        super().__init__(card=build_python_agent_card(base_url), store=store)

    async def execute(self, task: Task, message: Message) -> None:
        text = self._get_text(message)
        lower = text.lower()

        if any(kw in lower for kw in self.SKILL_KEYWORDS["python-review"]):
            await self._review(task, text)
        elif any(kw in lower for kw in self.SKILL_KEYWORDS["python-debug"]):
            await self._debug(task, text)
        elif any(kw in lower for kw in self.SKILL_KEYWORDS["python-test"]):
            await self._test(task, text)
        else:
            await self._write(task, text)

    async def _write(self, task: Task, prompt: str) -> None:
        from a2a.agent_sdk import run_agent_query
        code = await run_agent_query("python-developer", f"Write Python code for: {prompt}") or _stub_python(prompt)
        self.store.add_artifact(task.id, TaskArtifact(
            name="python-code.py",
            parts=[TextPart(type=PartType.TEXT, text=code)],
        ))
        self._reply(task.id, "Python implementation complete. See artifact.")

    async def _review(self, task: Task, prompt: str) -> None:
        from a2a.agent_sdk import run_agent_query
        review = await run_agent_query("python-developer", f"Review this Python code for bugs, security issues, and style: {prompt}") or _stub_review(prompt, "Python")
        self._add_text_artifact(task.id, review, name="python-review.md")
        self._reply(task.id, "Code review complete.")

    async def _debug(self, task: Task, prompt: str) -> None:
        from a2a.agent_sdk import run_agent_query
        analysis = await run_agent_query("python-developer", f"Debug this Python error and identify the root cause: {prompt}") or _stub_debug(prompt, "Python")
        self._add_text_artifact(task.id, analysis, name="debug-analysis.md")
        self._reply(task.id, "Debug analysis complete.")

    async def _test(self, task: Task, prompt: str) -> None:
        from a2a.agent_sdk import run_agent_query
        tests = await run_agent_query("python-developer", f"Write a pytest test suite for: {prompt}") or _stub_tests(prompt)
        self.store.add_artifact(task.id, TaskArtifact(
            name="test_generated.py",
            parts=[TextPart(type=PartType.TEXT, text=tests)],
        ))
        self._reply(task.id, "pytest test suite generated.")

    @staticmethod
    def _get_text(message: Message) -> str:
        parts = []
        for part in message.parts:
            if isinstance(part, TextPart):
                parts.append(part.text)
        return " ".join(parts)


# ─── Stub fallbacks (used if SDK query returns None) ─────────────────────────

def _stub_python(prompt: str) -> str:
    return (
        f'"""\nGenerated Python module.\nTask: {prompt[:120]}\n"""\n\n'
        "# TODO: SDK query returned no result\n\n\n"
        "def main() -> None:\n"
        '    """Entry point."""\n'
        "    pass\n\n\n"
        'if __name__ == "__main__":\n'
        "    main()\n"
    )


def _stub_review(prompt: str, lang: str) -> str:
    return f"## {lang} Code Review\n\n**Input:** {prompt[:200]}\n\n*(SDK query returned no result)*"


def _stub_debug(prompt: str, lang: str) -> str:
    return f"## {lang} Debug Analysis\n\n**Trace:** {prompt[:300]}\n\n*(SDK query returned no result)*"


def _stub_tests(prompt: str) -> str:
    return (
        '"""Generated pytest suite."""\n'
        "import pytest\n\n\n"
        "class TestGenerated:\n"
        f'    """Tests for: {prompt[:80]}"""\n\n'
        "    def test_placeholder(self) -> None:\n"
        "        # TODO: SDK query returned no result\n"
        "        assert True\n"
    )


def _stub_cpp(prompt: str) -> str:
    return (
        f"// Generated C++ module\n"
        f"// Task: {prompt[:120]}\n\n"
        "#include <iostream>\n"
        "#include <string>\n"
        "#include <memory>\n\n"
        "// TODO: SDK query returned no result\n\n"
        "int main() {\n"
        '    std::cout << "Hello from CppDeveloperAgent\\n";\n'
        "    return 0;\n"
        "}\n"
    )


# ─── C++ Developer Agent ──────────────────────────────────────────────────────

def build_cpp_agent_card(base_url: str = "http://localhost:8002") -> AgentCard:
    return AgentCard(
        name="CppDeveloper",
        description="Expert C++ developer — writes, reviews, and optimizes C++ code.",
        url=base_url,
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True),
        authentication=AgentAuthentication(schemes=[AuthScheme.ED25519]),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="cpp-write",
                name="Write C++",
                description="Write C++17/20/23 code, headers, and CMake configs.",
                tags=["cpp", "c++", "code", "write", "develop", "implement"],
                examples=["Write a C++ Ed25519 signer", "Implement a ring buffer in C++20"],
            ),
            AgentSkill(
                id="cpp-review",
                name="Review C++",
                description="Review C++ code for memory safety, UB, and performance.",
                tags=["cpp", "c++", "review", "audit", "memory", "security"],
                examples=["Review this C++ for memory leaks"],
            ),
            AgentSkill(
                id="cpp-debug",
                name="Debug C++",
                description="Diagnose C++ crashes, UB, and memory errors.",
                tags=["cpp", "c++", "debug", "segfault", "asan", "valgrind"],
                examples=["Debug this segfault", "Analyze this ASAN report"],
            ),
            AgentSkill(
                id="cpp-optimize",
                name="Optimize C++",
                description="Profile and optimize C++ for speed and memory.",
                tags=["cpp", "c++", "optimize", "performance", "perf", "simd"],
                examples=["Optimize this hot loop", "Add SIMD to this function"],
            ),
        ],
        provider={"name": "cybersecsuite", "url": base_url},
    )


class CppDeveloperAgent(BaseA2AAgent):
    """Specialized agent for C++ development tasks."""

    SKILL_KEYWORDS = {
        "cpp-review":   ("review", "audit", "check", "memory", "leak"),
        "cpp-debug":    ("debug", "segfault", "crash", "asan", "valgrind", "undefined"),
        "cpp-optimize": ("optimize", "performance", "perf", "simd", "vectorize", "fast"),
    }

    def __init__(self, base_url: str = "http://localhost:8002", store: Optional[TaskStore] = None) -> None:
        super().__init__(card=build_cpp_agent_card(base_url), store=store)

    async def execute(self, task: Task, message: Message) -> None:
        text = self._get_text(message)
        lower = text.lower()

        if any(kw in lower for kw in self.SKILL_KEYWORDS["cpp-review"]):
            await self._review(task, text)
        elif any(kw in lower for kw in self.SKILL_KEYWORDS["cpp-debug"]):
            await self._debug(task, text)
        elif any(kw in lower for kw in self.SKILL_KEYWORDS["cpp-optimize"]):
            await self._optimize(task, text)
        else:
            await self._write(task, text)

    async def _write(self, task: Task, prompt: str) -> None:
        from a2a.agent_sdk import run_agent_query
        code = await run_agent_query("cpp-developer", f"Write C++20 code for: {prompt}") or _stub_cpp(prompt)
        self.store.add_artifact(task.id, TaskArtifact(
            name="generated.cpp",
            parts=[TextPart(type=PartType.TEXT, text=code)],
        ))
        self._reply(task.id, "C++ implementation complete. See artifact.")

    async def _review(self, task: Task, prompt: str) -> None:
        from a2a.agent_sdk import run_agent_query
        review = await run_agent_query("cpp-developer", f"Review this C++ code for memory safety, UB, and security issues: {prompt}") or _stub_review(prompt, "C++")
        self._add_text_artifact(task.id, review, name="cpp-review.md")
        self._reply(task.id, "C++ code review complete.")

    async def _debug(self, task: Task, prompt: str) -> None:
        from a2a.agent_sdk import run_agent_query
        analysis = await run_agent_query("cpp-developer", f"Debug this C++ crash or error and identify root cause: {prompt}") or _stub_debug(prompt, "C++")
        self._add_text_artifact(task.id, analysis, name="debug-analysis.md")
        self._reply(task.id, "C++ debug analysis complete.")

    async def _optimize(self, task: Task, prompt: str) -> None:
        from a2a.agent_sdk import run_agent_query
        tips = await run_agent_query("cpp-developer", f"Provide C++ performance optimization recommendations for: {prompt}") or _stub_review(prompt, "C++ Optimization")
        self._add_text_artifact(task.id, tips, name="optimization-report.md")
        self._reply(task.id, "C++ optimization report complete.")

    @staticmethod
    def _get_text(message: Message) -> str:
        parts = []
        for part in message.parts:
            if isinstance(part, TextPart):
                parts.append(part.text)
        return " ".join(parts)


# ─── Convenience: build a pre-wired registry ─────────────────────────────────

def create_default_registry(
    base_url: str = "http://localhost:8000",
    load_claude_agents: bool = True,
    project_root: Optional["Path"] = None,  # type: ignore[name-defined]
) -> "AgentRegistry":
    """
    Create a registry pre-populated from .claude/agents/*.md definitions.

    All agent cards (cybersec-analyst, python-developer, cpp-developer,
    filesystem-analyst, kernel-analyst, memory-analyst, network-analyst,
    persistence-analyst, threat-modeler, hunter) are loaded dynamically
    from the .claude/agents/ directory — no hardcoded registrations needed.

    Args:
        base_url:           Base URL for all local agent cards.
        load_claude_agents: Load from .claude/agents/ (default True).
        project_root:       Override project root for .claude discovery.
    """
    from pathlib import Path as _Path
    from a2a.registry import AgentRegistry

    registry = AgentRegistry()

    if load_claude_agents:
        from a2a.agent_loader import load_cybersecsuite_agents
        load_cybersecsuite_agents(
            registry,
            project_root=_Path(str(project_root)) if project_root else None,
            base_url=base_url,
        )

    return registry

