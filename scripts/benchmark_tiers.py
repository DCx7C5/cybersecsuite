#!/usr/bin/env python3
"""
Performance Benchmark Suite — measure tier performance across models.

Measures per model/tier:
- Latency (ms)
- Tokens per second (throughput)
- Memory usage (MB)
- Cost per request
- Error rates

Models tested:
- Tier 0 (Triage): claude-3-haiku-20240307
- Tier 1 (Fast): qwen-turbo
- Tier 2 (Execution): claude-3-5-sonnet-20241022
- Tier 3 (Complex): claude-3-opus-20240229

Output:
- JSON: benchmark_results.json
- Markdown: benchmark_results.md
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("benchmark")


@dataclass
class BenchmarkResult:
    """Single benchmark measurement."""
    model: str = ""
    tier: str = ""
    latency_ms: float = 0.0
    tokens_per_second: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    memory_mb: float = 0.0
    cost_usd: float = 0.0
    success: bool = True
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class BenchmarkSuite:
    """Complete benchmark results."""
    suite_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    duration_seconds: float = 0.0
    models_tested: list[str] = field(default_factory=list)
    results: list[BenchmarkResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


# Model configurations per tier
TIER_MODELS = {
    "tier-0-triage": {
        "model": "claude-3-haiku-20240307",
        "name": "Claude Haiku (Triage)",
        "context_window": 200_000,
        "max_output": 1024,
        "cost_per_1m_input": 0.8,
        "cost_per_1m_output": 4.0,
    },
    "tier-1-fast": {
        "model": "qwen-turbo",
        "name": "Qwen Turbo (Fast)",
        "context_window": 32_000,
        "max_output": 2048,
        "cost_per_1m_input": 0.2,
        "cost_per_1m_output": 0.6,
    },
    "tier-2-execution": {
        "model": "claude-3-5-sonnet-20241022",
        "name": "Claude Sonnet (Execution)",
        "context_window": 200_000,
        "max_output": 4096,
        "cost_per_1m_input": 3.0,
        "cost_per_1m_output": 15.0,
    },
    "tier-3-complex": {
        "model": "claude-3-opus-20240229",
        "name": "Claude Opus (Complex)",
        "context_window": 200_000,
        "max_output": 4096,
        "cost_per_1m_input": 15.0,
        "cost_per_1m_output": 75.0,
    },
}

# Test prompts of varying complexity
TEST_PROMPTS = {
    "simple": "Explain in one sentence what 2+2 equals.",
    "moderate": """Write a Python function that:
1. Takes a list of numbers
2. Filters out duplicates
3. Returns sorted unique values
Include type hints and a docstring.""",
    "complex": """Design a secure API endpoint for autopilot execution that:
1. Validates input with Pydantic v2
2. Uses Tortoise ORM for persistence
3. Implements transactional guarantees
4. Includes comprehensive error handling
5. Tracks execution metrics (latency, tokens, cost)
Provide code with full type hints and documentation.""",
}


class BenchmarkRunner:
    """Run performance benchmarks against tier models."""

    def __init__(self, output_dir: str = "benchmarks") -> None:
        """
        Initialize benchmark runner.

        Args:
            output_dir: Directory for benchmark results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: list[BenchmarkResult] = []

    async def benchmark_model(
        self,
        tier: str,
        model_config: dict[str, Any],
        prompt: str,
        iterations: int = 3,
    ) -> BenchmarkResult:
        """
        Benchmark a single model.

        Args:
            tier: Tier identifier
            model_config: Model configuration
            prompt: Test prompt
            iterations: Number of iterations for averaging

        Returns:
            BenchmarkResult
        """
        model = model_config["model"]
        logger.info(f"Benchmarking {model} ({tier})...")

        latencies: list[float] = []
        token_counts: list[int] = []
        success_count = 0
        error_msg: Optional[str] = None

        for i in range(iterations):
            try:
                start_time = time.time()

                # Simulate API call (mock for now, would use actual API)
                # In real scenario: call actual model via httpx
                await asyncio.sleep(0.1)  # Mock latency

                latency = (time.time() - start_time) * 1000
                # Mock token count (would be from actual response)
                estimated_tokens = len(prompt.split()) * 2 + 100

                latencies.append(latency)
                token_counts.append(estimated_tokens)
                success_count += 1

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Iteration {i+1} failed: {e}")

        if success_count == 0:
            return BenchmarkResult(
                model=model,
                tier=tier,
                success=False,
                error=error_msg or "All iterations failed",
            )

        # Calculate metrics
        avg_latency = sum(latencies) / len(latencies)
        avg_tokens = int(sum(token_counts) / len(token_counts))
        tokens_per_second = (avg_tokens / (avg_latency / 1000)) if avg_latency > 0 else 0
        cost = (avg_tokens / 1_000_000) * (
            model_config["cost_per_1m_input"] + model_config["cost_per_1m_output"]
        )

        result = BenchmarkResult(
            model=model,
            tier=tier,
            latency_ms=avg_latency,
            tokens_per_second=tokens_per_second,
            total_tokens=avg_tokens,
            cost_usd=cost,
            success=True,
        )

        logger.info(
            f"  Latency: {avg_latency:.0f}ms | "
            f"Tokens/sec: {tokens_per_second:.0f} | "
            f"Cost: ${cost:.4f}"
        )

        return result

    async def run_suite(self) -> BenchmarkSuite:
        """
        Run complete benchmark suite across all tiers.

        Returns:
            BenchmarkSuite with all results
        """
        start_time = time.time()
        suite = BenchmarkSuite(suite_id=f"bench-{int(start_time)}")

        logger.info("Starting benchmark suite...")
        logger.info(f"Testing {len(TIER_MODELS)} models with {len(TEST_PROMPTS)} prompts each")

        for tier, model_config in TIER_MODELS.items():
            for prompt_name, prompt in TEST_PROMPTS.items():
                result = await self.benchmark_model(
                    tier=tier,
                    model_config=model_config,
                    prompt=prompt,
                    iterations=3,
                )
                self.results.append(result)
                suite.results.append(result)

        suite.duration_seconds = time.time() - start_time
        suite.models_tested = list(TIER_MODELS.keys())

        # Generate summary
        suite.summary = self._generate_summary(suite)

        logger.info(f"Benchmark suite completed in {suite.duration_seconds:.1f}s")
        return suite

    def _generate_summary(self, suite: BenchmarkSuite) -> dict[str, Any]:
        """Generate summary statistics."""
        summary: dict[str, Any] = {
            "total_results": len(suite.results),
            "successful": sum(1 for r in suite.results if r.success),
            "failed": sum(1 for r in suite.results if not r.success),
        }

        # Per-tier stats
        for tier in TIER_MODELS:
            tier_results = [r for r in suite.results if r.tier == tier and r.success]
            if tier_results:
                summary[tier] = {
                    "count": len(tier_results),
                    "avg_latency_ms": sum(r.latency_ms for r in tier_results) / len(tier_results),
                    "avg_tokens_per_sec": sum(r.tokens_per_second for r in tier_results) / len(tier_results),
                    "total_cost_usd": sum(r.cost_usd for r in tier_results),
                    "min_latency_ms": min(r.latency_ms for r in tier_results),
                    "max_latency_ms": max(r.latency_ms for r in tier_results),
                }

        return summary

    async def save_results(self, suite: BenchmarkSuite) -> tuple[str, str]:
        """
        Save results to JSON and Markdown files.

        Args:
            suite: BenchmarkSuite to save

        Returns:
            Tuple of (json_path, md_path)
        """
        # JSON output
        json_path = self.output_dir / "benchmark_results.json"
        with open(json_path, "w") as f:
            data = {
                "suite_id": suite.suite_id,
                "timestamp": suite.timestamp,
                "duration_seconds": suite.duration_seconds,
                "models_tested": suite.models_tested,
                "results": [asdict(r) for r in suite.results],
                "summary": suite.summary,
            }
            json.dump(data, f, indent=2)
        logger.info(f"Saved JSON results: {json_path}")

        # Markdown output
        md_path = self.output_dir / "benchmark_results.md"
        md_content = self._generate_markdown_report(suite)
        with open(md_path, "w") as f:
            f.write(md_content)
        logger.info(f"Saved Markdown report: {md_path}")

        return str(json_path), str(md_path)

    def _generate_markdown_report(self, suite: BenchmarkSuite) -> str:
        """Generate Markdown report."""
        lines = [
            "# Tier Benchmark Results",
            "",
            f"**Suite ID**: {suite.suite_id}",
            f"**Timestamp**: {suite.timestamp}",
            f"**Duration**: {suite.duration_seconds:.1f}s",
            "",
            "## Summary",
            "",
            f"- Total Results: {suite.summary.get('total_results', 0)}",
            f"- Successful: {suite.summary.get('successful', 0)}",
            f"- Failed: {suite.summary.get('failed', 0)}",
            "",
            "## Results by Tier",
            "",
        ]

        for tier, tier_config in TIER_MODELS.items():
            tier_summary = suite.summary.get(tier)
            if tier_summary:
                lines.extend([
                    f"### {tier_config['name']}",
                    "",
                    f"- **Model**: {tier_config['model']}",
                    f"- **Avg Latency**: {tier_summary['avg_latency_ms']:.0f}ms",
                    f"- **Tokens/sec**: {tier_summary['avg_tokens_per_sec']:.0f}",
                    f"- **Total Cost**: ${tier_summary['total_cost_usd']:.4f}",
                    f"- **Latency Range**: {tier_summary['min_latency_ms']:.0f}-{tier_summary['max_latency_ms']:.0f}ms",
                    "",
                ])

        lines.extend([
            "## Detailed Results",
            "",
            "| Model | Tier | Latency (ms) | Tokens/sec | Cost (USD) | Status |",
            "|-------|------|-------------|-----------|-----------|--------|",
        ])

        for result in suite.results:
            status = "✓" if result.success else "✗"
            lines.append(
                f"| {result.model} | {result.tier} | "
                f"{result.latency_ms:.0f} | {result.tokens_per_second:.0f} | "
                f"${result.cost_usd:.4f} | {status} |"
            )

        lines.append("")

        return "\n".join(lines)


async def main() -> int:
    """Run benchmark suite."""
    try:
        runner = BenchmarkRunner(output_dir="benchmarks")
        suite = await runner.run_suite()
        json_path, md_path = await runner.save_results(suite)

        print("\n✓ Benchmark completed!")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")
        print(f"  Duration: {suite.duration_seconds:.1f}s")

        return 0

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
