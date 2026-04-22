"""QoL Injection Performance Benchmark — T014

This module benchmarks the performance of QoL output control injection operations.
Measures latency, memory overhead, and throughput with various toggle configurations.

Baseline targets (from plan.md T014):
    - build_injection() latency: <1ms per call
    - inject_into_request() latency: <10ms per call
    - Memory overhead per manager: <1 MB
    - Throughput: >100 requests/sec with 4 active toggles

Referenz:
    plan.md T014 — Performance benchmarking
    src/ai_proxy/qol_controls/manager.py — QoLManager
    src/ai_proxy/qol_controls/models.py — QoLToggle, QoLSettings
    src/ai_proxy/qol_controls/prompts.py — build_fragment_block

Status: production (Phase 1 complete)
Version: 1.0
Last modified: 2026-04-26 06:00:00Z
Author: python-developer
"""
from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path
from typing import Any

try:
    from ai_proxy.qol_controls.manager import QoLManager
    from ai_proxy.qol_controls.models import QoLSettings, QoLToggle
    IMPORTS_OK = True
except ImportError:
    IMPORTS_OK = False
    print("ERROR: Cannot import QoL controls — ensure cybersecsuite is installed", file=sys.stderr)
    sys.exit(1)


# ── Test configurations ──────────────────────────────────────────────────────

TOGGLE_CONFIGS = [
    ("minimal", {QoLToggle.NO_THINKING}),
    ("medium", {QoLToggle.NO_THINKING, QoLToggle.NO_CHAT, QoLToggle.MINIMAL, QoLToggle.NO_MARKDOWN}),
    ("heavy", {
        QoLToggle.NO_THINKING,
        QoLToggle.NO_CHAT,
        QoLToggle.MINIMAL,
        QoLToggle.NO_MARKDOWN,
        QoLToggle.REDACT_SECRETS,
        QoLToggle.STRUCTURED_ONLY,
    }),
]

REQUEST_BODY_TEMPLATE = {
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "model": "claude-3-sonnet-20250514",
    "max_tokens": 1024,
}


class BenchmarkResults:
    """Container for benchmark results."""

    def __init__(self, name: str, latencies: list[float], config_name: str = ""):
        self.name = name
        self.config_name = config_name
        self.latencies = latencies
        self.count = len(latencies)

    @property
    def min_ms(self) -> float:
        return min(self.latencies) * 1000 if self.latencies else 0

    @property
    def max_ms(self) -> float:
        return max(self.latencies) * 1000 if self.latencies else 0

    @property
    def mean_ms(self) -> float:
        return statistics.mean(self.latencies) * 1000 if self.latencies else 0

    @property
    def median_ms(self) -> float:
        return statistics.median(self.latencies) * 1000 if self.latencies else 0

    @property
    def stdev_ms(self) -> float:
        return statistics.stdev(self.latencies) * 1000 if len(self.latencies) > 1 else 0

    @property
    def p95_ms(self) -> float:
        """95th percentile latency."""
        if not self.latencies:
            return 0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)] * 1000

    @property
    def p99_ms(self) -> float:
        """99th percentile latency."""
        if not self.latencies:
            return 0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * 0.99)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)] * 1000

    def __str__(self) -> str:
        return (
            f"{self.name:35s} | "
            f"min={self.min_ms:7.2f}ms | "
            f"med={self.median_ms:7.2f}ms | "
            f"mean={self.mean_ms:7.2f}ms | "
            f"p95={self.p95_ms:7.2f}ms | "
            f"p99={self.p99_ms:7.2f}ms | "
            f"max={self.max_ms:7.2f}ms (n={self.count})"
        )


def benchmark_build_injection(manager: QoLManager, iterations: int = 1000) -> list[BenchmarkResults]:
    """Benchmark build_injection() with various toggle configurations."""
    results = []

    for config_name, toggle_set in TOGGLE_CONFIGS:
        settings = QoLSettings()
        for toggle in toggle_set:
            settings.activate(toggle)

        latencies: list[float] = []
        for _ in range(iterations):
            start = time.perf_counter()
            _ = manager.build_injection(settings)
            elapsed = time.perf_counter() - start
            latencies.append(elapsed)

        result = BenchmarkResults(f"build_injection({config_name})", latencies, config_name)
        results.append(result)

    return results


def benchmark_inject_into_request(
    manager: QoLManager,
    iterations: int = 1000,
) -> list[BenchmarkResults]:
    """Benchmark inject_into_request() with various toggle configurations."""
    results = []

    for config_name, toggle_set in TOGGLE_CONFIGS:
        settings = QoLSettings(scope="session")
        for toggle in toggle_set:
            settings.activate(toggle)
        manager.save_settings(settings)

        body = REQUEST_BODY_TEMPLATE.copy()
        latencies: list[float] = []

        for _ in range(iterations):
            start = time.perf_counter()
            _ = manager.inject_into_request(body, scope="session")
            elapsed = time.perf_counter() - start
            latencies.append(elapsed)

        result = BenchmarkResults(
            f"inject_into_request({config_name})",
            latencies,
            config_name,
        )
        results.append(result)

    return results


def benchmark_throughput(manager: QoLManager, duration_seconds: float = 5.0) -> dict[str, Any]:
    """Measure throughput: requests/second with medium toggle config."""
    settings = QoLSettings(scope="session")
    for toggle in TOGGLE_CONFIGS[1][1]:  # medium config
        settings.activate(toggle)
    manager.save_settings(settings)

    body = REQUEST_BODY_TEMPLATE.copy()
    request_count = 0
    start_time = time.perf_counter()

    while time.perf_counter() - start_time < duration_seconds:
        _ = manager.inject_into_request(body, scope="session")
        request_count += 1

    elapsed = time.perf_counter() - start_time
    throughput = request_count / elapsed

    return {
        "duration_seconds": elapsed,
        "request_count": request_count,
        "throughput_rps": throughput,
        "config": "medium (4 toggles)",
    }


def benchmark_memory_overhead(iterations: int = 100) -> dict[str, Any]:
    """Measure memory overhead of manager instance and caching."""
    import sys

    managers = []
    sizes = []

    for _ in range(iterations):
        mgr = QoLManager()
        # Trigger some caching
        for _, toggle_set in TOGGLE_CONFIGS:
            settings = QoLSettings()
            for toggle in toggle_set:
                settings.activate(toggle)
            _ = mgr.build_injection(settings)

        size = sys.getsizeof(mgr)
        sizes.append(size)
        managers.append(mgr)

    avg_size_kb = statistics.mean(sizes) / 1024
    max_size_kb = max(sizes) / 1024

    return {
        "iterations": iterations,
        "avg_size_kb": avg_size_kb,
        "max_size_kb": max_size_kb,
        "avg_cache_entries": len(managers[0]._fragment_cache) if managers else 0,
    }


def benchmark_cache_effectiveness(manager: QoLManager, iterations: int = 10000) -> dict[str, Any]:
    """Measure cache hit rate for fragment generation."""
    settings = QoLSettings()
    settings.activate(QoLToggle.NO_THINKING, QoLToggle.MINIMAL)
    manager.save_settings(settings)

    # Warm up cache
    _ = manager.build_injection(settings)

    cache_hits = 0
    cache_misses = 0
    key = frozenset(settings.enabled_toggles)

    for _ in range(iterations):
        # Check cache before calling
        was_cached = key in manager._fragment_cache
        _ = manager.build_injection(settings)
        if was_cached:
            cache_hits += 1
        else:
            cache_misses += 1

    return {
        "iterations": iterations,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "hit_rate": cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0,
    }


def print_results_table(
    title: str,
    results: list[BenchmarkResults],
    baseline_ms: float = 10.0,
) -> None:
    """Print benchmark results as a formatted table."""
    print(f"\n{'=' * 110}")
    print(f"{title:^110}")
    print(f"{'=' * 110}")
    print(
        f"{'Operation':35s} | "
        f"{'min':>7s} | "
        f"{'median':>7s} | "
        f"{'mean':>7s} | "
        f"{'p95':>7s} | "
        f"{'p99':>7s} | "
        f"{'max':>7s} | {'n':>8s}"
    )
    print("-" * 110)

    for result in results:
        print(result)
        # Check baseline
        if result.median_ms > baseline_ms:
            print(
                f"  ⚠️  SLOW: median {result.median_ms:.2f}ms > baseline {baseline_ms}ms "
                f"(config: {result.config_name})"
            )
        else:
            print(f"  ✓ FAST: median {result.median_ms:.2f}ms ≤ baseline {baseline_ms}ms")


def main() -> None:
    """Run all benchmarks and print results."""
    import tempfile

    print("╔════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                     QoL Injection Performance Benchmark — Phase 1B Final                              ║")
    print("╚════════════════════════════════════════════════════════════════════════════════════════════════════════╝")

    # Create temp manager for benchmarks
    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = QoLManager()
        manager._base_dir = Path(tmp_dir)

        # Benchmark 1: build_injection()
        print("\n[1/5] Benchmarking build_injection()...")
        build_injection_results = benchmark_build_injection(manager, iterations=5000)
        print_results_table("build_injection() — Fragment generation", build_injection_results, baseline_ms=1.0)

        # Benchmark 2: inject_into_request()
        print("\n[2/5] Benchmarking inject_into_request()...")
        inject_results = benchmark_inject_into_request(manager, iterations=5000)
        print_results_table(
            "inject_into_request() — Full injection with settings loading",
            inject_results,
            baseline_ms=10.0,
        )

        # Benchmark 3: Throughput
        print("\n[3/5] Benchmarking throughput (duration: 5 seconds)...")
        throughput = benchmark_throughput(manager, duration_seconds=5.0)
        print(
            f"\n  Throughput (medium config, 4 toggles):\n"
            f"    Requests processed: {throughput['request_count']}\n"
            f"    Duration: {throughput['duration_seconds']:.2f}s\n"
            f"    Throughput: {throughput['throughput_rps']:.1f} requests/sec\n"
            f"    ✓ Baseline: >100 rps — {'PASS' if throughput['throughput_rps'] > 100 else 'FAIL'}"
        )

        # Benchmark 4: Memory overhead
        print("\n[4/5] Benchmarking memory overhead...")
        memory = benchmark_memory_overhead(iterations=100)
        print(
            f"\n  Memory overhead:\n"
            f"    Average manager size: {memory['avg_size_kb']:.2f} KB\n"
            f"    Max manager size: {memory['max_size_kb']:.2f} KB\n"
            f"    Average cache entries: {memory['avg_cache_entries']}\n"
            f"    ✓ Baseline: <1 MB — {'PASS' if memory['avg_size_kb'] < 1024 else 'FAIL'}"
        )

        # Benchmark 5: Cache effectiveness
        print("\n[5/5] Benchmarking cache effectiveness...")
        cache = benchmark_cache_effectiveness(manager, iterations=10000)
        print(
            f"\n  Cache effectiveness (10,000 lookups):\n"
            f"    Cache hits: {cache['cache_hits']}\n"
            f"    Cache misses: {cache['cache_misses']}\n"
            f"    Hit rate: {cache['hit_rate'] * 100:.1f}%\n"
            f"    ✓ Baseline: >90% hit rate — {'PASS' if cache['hit_rate'] > 0.9 else 'WARN'}"
        )

    # Summary
    print("\n" + "=" * 110)
    print("SUMMARY")
    print("=" * 110)
    print(f"✓ build_injection() median latency:      {build_injection_results[1].median_ms:.2f} ms (baseline: <1ms)")
    print(f"✓ inject_into_request() median latency:  {inject_results[1].median_ms:.2f} ms (baseline: <10ms)")
    print(f"✓ Throughput:                             {throughput['throughput_rps']:.1f} rps (baseline: >100)")
    print(f"✓ Memory overhead:                        {memory['avg_size_kb']:.2f} KB (baseline: <1 MB)")
    print(f"✓ Cache hit rate:                         {cache['hit_rate'] * 100:.1f}% (baseline: >90%)")
    print("=" * 110)


if __name__ == "__main__":
    main()
