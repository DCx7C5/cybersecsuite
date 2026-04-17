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
        code = self._generate_python(prompt)
        self.store.add_artifact(task.id, TaskArtifact(
            name="python-code.py",
            parts=[TextPart(type=PartType.TEXT, text=code)],
        ))
        self._reply(task.id, "Python implementation complete. See artifact.")

    async def _review(self, task: Task, prompt: str) -> None:
        review = (
            f"## Python Code Review\n\n"
            f"**Input:** {prompt[:200]}...\n\n"
            "### Findings\n"
            "- Check for SQL injection via parameterized queries\n"
            "- Validate all external inputs\n"
            "- Ensure secrets are loaded from env, not hardcoded\n"
            "- Use `blake2b` instead of MD5/SHA1 for integrity\n\n"
            "*(Wire to an LLM for full static analysis)*"
        )
        self._add_text_artifact(task.id, review, name="python-review.md")
        self._reply(task.id, "Code review complete.")

    async def _debug(self, task: Task, prompt: str) -> None:
        analysis = (
            f"## Python Debug Analysis\n\n"
            f"**Trace:** {prompt[:300]}\n\n"
            "### Likely Cause\n"
            "- Check import paths and virtual environment activation\n"
            "- Verify async/await usage is consistent\n"
            "- Inspect None dereferences with `assert x is not None`\n\n"
            "*(Wire to an LLM for exact root cause)*"
        )
        self._add_text_artifact(task.id, analysis, name="debug-analysis.md")
        self._reply(task.id, "Debug analysis complete.")

    async def _test(self, task: Task, prompt: str) -> None:
        tests = self._generate_tests(prompt)
        self.store.add_artifact(task.id, TaskArtifact(
            name="test_generated.py",
            parts=[TextPart(type=PartType.TEXT, text=tests)],
        ))
        self._reply(task.id, "pytest test suite generated.")

    @staticmethod
    def _generate_python(prompt: str) -> str:
        return (
            f'"""\nGenerated Python module.\nTask: {prompt[:120]}\n"""\n\n'
            "# TODO: implement with LLM backend\n\n\n"
            "def main() -> None:\n"
            '    """Entry point."""\n'
            "    pass\n\n\n"
            'if __name__ == "__main__":\n'
            "    main()\n"
        )

    @staticmethod
    def _generate_tests(prompt: str) -> str:
        return (
            '"""Generated pytest suite."""\n'
            "import pytest\n\n\n"
            "class TestGenerated:\n"
            f'    """Tests for: {prompt[:80]}"""\n\n'
            "    def test_placeholder(self) -> None:\n"
            "        # TODO: implement with LLM backend\n"
            "        assert True\n"
        )

    @staticmethod
    def _get_text(message: Message) -> str:
        parts = []
        for part in message.parts:
            if isinstance(part, TextPart):
                parts.append(part.text)
        return " ".join(parts)


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
        code = self._generate_cpp(prompt)
        self.store.add_artifact(task.id, TaskArtifact(
            name="generated.cpp",
            parts=[TextPart(type=PartType.TEXT, text=code)],
        ))
        self._reply(task.id, "C++ implementation complete. See artifact.")

    async def _review(self, task: Task, prompt: str) -> None:
        review = (
            "## C++ Code Review\n\n"
            "### Memory Safety\n"
            "- Prefer `std::unique_ptr` / `std::shared_ptr` over raw `new`\n"
            "- Check array bounds — use `.at()` or `std::span`\n"
            "- Avoid `reinterpret_cast` without strict aliasing justification\n\n"
            "### Security\n"
            "- Sanitize all external inputs (buffer overflows)\n"
            "- Use `-D_FORTIFY_SOURCE=2 -fstack-protector-strong` in build\n"
            "- Run with AddressSanitizer: `-fsanitize=address,undefined`\n\n"
            "*(Wire to an LLM for full static analysis)*"
        )
        self._add_text_artifact(task.id, review, name="cpp-review.md")
        self._reply(task.id, "C++ code review complete.")

    async def _debug(self, task: Task, prompt: str) -> None:
        analysis = (
            "## C++ Debug Analysis\n\n"
            "### Steps\n"
            "1. Compile with `-g -fsanitize=address,undefined`\n"
            "2. Run under `valgrind --leak-check=full`\n"
            "3. Check for dangling references and use-after-free\n"
            "4. Inspect with `gdb -ex run -ex bt ./binary`\n\n"
            "*(Wire to an LLM for exact root cause)*"
        )
        self._add_text_artifact(task.id, analysis, name="debug-analysis.md")
        self._reply(task.id, "C++ debug analysis complete.")

    async def _optimize(self, task: Task, prompt: str) -> None:
        tips = (
            "## C++ Optimization Report\n\n"
            "### Quick Wins\n"
            "- Enable `-O3 -march=native` in release builds\n"
            "- Use `[[likely]]` / `[[unlikely]]` hints on branches\n"
            "- Prefer `std::array` over `std::vector` for fixed-size data\n"
            "- Consider SIMD via `<immintrin.h>` or `std::experimental::simd`\n"
            "- Profile with `perf stat` / `perf record` before micro-optimizing\n\n"
            "*(Wire to an LLM + profiler output for detailed recommendations)*"
        )
        self._add_text_artifact(task.id, tips, name="optimization-report.md")
        self._reply(task.id, "C++ optimization report complete.")

    @staticmethod
    def _generate_cpp(prompt: str) -> str:
        return (
            f"// Generated C++ module\n"
            f"// Task: {prompt[:120]}\n\n"
            "#include <iostream>\n"
            "#include <string>\n"
            "#include <memory>\n\n"
            "// TODO: implement with LLM backend\n\n"
            "int main() {\n"
            '    std::cout << "Hello from CppDeveloperAgent\\n";\n'
            "    return 0;\n"
            "}\n"
        )

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

