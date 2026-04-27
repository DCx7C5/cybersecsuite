"""
CLI interface for the AI Proxy.

Provides commands for provider management, usage reporting, cost tracking,
and ad-hoc chat completions.

Usage:
    cybersec-proxy providers         # List configured providers
    cybersec-proxy models            # List available models
    cybersec-proxy usage             # Show usage summary
    cybersec-proxy cost              # Show cost breakdown
    cybersec-proxy chat "prompt"     # Send a chat completion
    cybersec-proxy chat "prompt" --model gpt-4o --provider openai
    cybersec-proxy chat "prompt" --free          # Use free providers only
    cybersec-proxy serve             # Start the proxy server
"""


import argparse
import asyncio
import json
import sys
from typing import Any


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _print_table(rows: list[dict[str, Any]], columns: list[str]) -> None:
    """Simple ASCII table printer."""
    if not rows:
        print("(no data)")
        return

    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))

    header = " | ".join(col.ljust(widths[col]) for col in columns)
    sep = "-+-".join("-" * widths[col] for col in columns)
    print(header)
    print(sep)
    for row in rows:
        line = " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
        print(line)


async def cmd_providers(args: argparse.Namespace) -> None:
    from src.registries.providers import get_all_providers

    providers = get_all_providers()
    rows = []
    for p in providers.values():
        has_key = p.get_api_key() is not None
        rows.append({
            "id": p.id,
            "name": p.name,
            "format": p.api_format.value,
            "free": "✓" if p.is_free else "",
            "key": "✓" if has_key else "✗",
            "models": len(p.models),
            "rpm": p.rate_limit_rpm,
        })

    _print_table(rows, ["id", "name", "format", "free", "key", "models", "rpm"])
    print(f"\n{len(rows)} providers total, {sum(1 for r in rows if r['key'] == '✓')} with API keys configured")


async def cmd_models(args: argparse.Namespace) -> None:
    from src.registries.providers import list_all_models

    models = list_all_models()
    if args.provider:
        models = [m for m in models if m["owned_by"] == args.provider]

    rows = []
    for m in models:
        rows.append({
            "model_id": m["id"],
            "provider": m["owned_by"],
            "context": f"{m['context_window']:,}",
            "max_out": f"{m['max_output']:,}",
        })

    _print_table(rows, ["model_id", "provider", "context", "max_out"])
    print(f"\n{len(rows)} models available")


async def cmd_usage(args: argparse.Namespace) -> None:
    from ai_proxy.services.usage_tracker import usage_tracker

    summary = usage_tracker.get_summary()
    print(f"Total tokens:   {summary['total_tokens']:,}")
    print(f"Total cost:     ${summary['total_cost_usd']:.6f}")
    print(f"Total requests: {summary['total_requests']}")
    print(f"Total errors:   {summary['total_errors']}")

    if summary["by_provider"]:
        print("\nBy provider:")
        rows = [
            {"provider": pid, **stats}
            for pid, stats in summary["by_provider"].items()
        ]
        _print_table(rows, ["provider", "tokens", "cost_usd", "requests", "errors"])

    recent = usage_tracker.get_recent(limit=args.limit)
    if recent:
        print(f"\nLast {len(recent)} requests:")
        _print_table(recent, ["provider", "model", "tokens", "cost_usd", "latency_ms", "success"])


async def cmd_cost(args: argparse.Namespace) -> None:
    from ai_proxy.services.usage_tracker import usage_tracker

    summary = usage_tracker.get_summary()
    print(f"💰 Total cost: ${summary['total_cost_usd']:.6f}")
    print(f"📊 Total tokens: {summary['total_tokens']:,}")

    if summary["by_provider"]:
        print("\nCost by provider:")
        for pid, stats in sorted(summary["by_provider"].items(), key=lambda x: x[1]["cost_usd"], reverse=True):
            print(f"  {pid:20s}  ${stats['cost_usd']:.6f}  ({stats['requests']} requests)")


async def cmd_chat(args: argparse.Namespace) -> None:
    from ai_proxy.routing.combo import smart_route, route_request, ComboConfig, ComboTarget, Strategy

    body: dict[str, Any] = {
        "model": args.model,
        "messages": [{"role": "user", "content": args.prompt}],
    }

    if args.system:
        body["messages"].insert(0, {"role": "system", "content": args.system})
    if args.temperature is not None:
        body["temperature"] = args.temperature
    if args.max_tokens:
        body["max_tokens"] = args.max_tokens

    if args.provider:
        combo = ComboConfig(
            id=f"cli-{args.provider}",
            name=f"CLI → {args.provider}",
            strategy=Strategy.PRIORITY,
            targets=[ComboTarget(provider_id=args.provider, model_id=args.model)],
        )
        result = await route_request(body, combo)
    else:
        result = await smart_route(
            body,
            prefer_free=args.free,
            max_cost_per_1k=args.max_cost,
        )

    if not result.ok:
        print(f"Error ({result.status_code}): {result.error}", file=sys.stderr)
        sys.exit(1)

    if result.body:
        choices = result.body.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")
            print(content)

        if args.verbose:
            usage = result.body.get("usage", {})
            proxy = result.body.get("_proxy", {})
            print(f"\n--- Provider: {proxy.get('provider', result.provider_id)}", file=sys.stderr)
            print(f"--- Model: {proxy.get('model', result.model_id)}", file=sys.stderr)
            print(f"--- Latency: {proxy.get('latency_ms', result.latency_ms):.0f}ms", file=sys.stderr)
            print(f"--- Tokens: {usage.get('total_tokens', 0)}", file=sys.stderr)


async def cmd_marketplace(args: argparse.Namespace) -> None:
    """Dispatch marketplace sub-commands."""
    from src.registries.marketplace import get_registry

    reg = get_registry()

    if args.mp_command == "list":
        kind = getattr(args, "kind", None)
        provider = getattr(args, "provider", None)
        items = list_items(kind=kind, provider=provider)
        rows = [
            {
                "id": i.id,
                "name": i.name,
                "kind": i.kind,
                "provider": i.provider,
                "status": i.status.value,
                "tags": ", ".join(i.tags),
            }
            for i in items
        ]
        _print_table(rows, ["id", "name", "kind", "provider", "status", "tags"])
        print(f"\n{len(rows)} item(s) in catalog")

    elif args.mp_command == "install":
        try:
            item = reg.install(args.item_id)
            print(f"✓ Installed {item.id!r} ({item.name}) — status: {item.status.value}")
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.mp_command == "uninstall":
        removed = reg.uninstall(args.item_id)
        if removed:
            print(f"✓ Uninstalled {args.item_id!r}")
        else:
            print(f"Error: {args.item_id!r} is not installed", file=sys.stderr)
            sys.exit(1)

    elif args.mp_command == "info":
        item = get_item(args.item_id)
        if item is None:
            print(f"Error: item {args.item_id!r} not found", file=sys.stderr)
            sys.exit(1)
        _print_json(item.model_dump(mode="json"))

    elif args.mp_command == "search":
        items = search(args.query)
        rows = [
            {
                "id": i.id,
                "name": i.name,
                "kind": i.kind,
                "provider": i.provider,
                "status": i.status.value,
            }
            for i in items
        ]
        _print_table(rows, ["id", "name", "kind", "provider", "status"])
        print(f"\n{len(rows)} result(s) for {args.query!r}")

    else:
        print("Unknown marketplace sub-command. Use: list, install, uninstall, info, search")


async def cmd_serve(args: argparse.Namespace) -> None:
    import uvicorn
    print(f"Starting AI proxy on {args.host}:{args.port}")
    print(f"  OpenAI-compatible: http://{args.host}:{args.port}/v1/chat/completions")
    print(f"  Models:            http://{args.host}:{args.port}/v1/models")
    print(f"  Providers:         http://{args.host}:{args.port}/v1/providers")
    print(f"  Usage:             http://{args.host}:{args.port}/v1/usage")
    print(f"  Health:            http://{args.host}:{args.port}/health")

    config = uvicorn.Config(
        "proxy.asgi:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cybersec-proxy",
        description="CyberSec AI Proxy — multi-provider LLM router with cost optimization",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # providers
    sub.add_parser("providers", help="List configured providers")

    # models
    m = sub.add_parser("models", help="List available models")
    m.add_argument("--provider", help="Filter by provider ID")

    # usage
    u = sub.add_parser("usage", help="Show usage summary")
    u.add_argument("--limit", type=int, default=10, help="Number of recent records")

    # cost
    sub.add_parser("cost", help="Show cost breakdown")

    # chat
    c = sub.add_parser("chat", help="Send a chat completion")
    c.add_argument("prompt", help="User prompt")
    c.add_argument("--model", default="gpt-4o-mini", help="Model ID (default: gpt-4o-mini)")
    c.add_argument("--provider", help="Force specific provider")
    c.add_argument("--system", help="System prompt")
    c.add_argument("--temperature", type=float, help="Temperature (0.0-2.0)")
    c.add_argument("--max-tokens", type=int, help="Max output tokens")
    c.add_argument("--free", action="store_true", help="Prefer free providers")
    c.add_argument("--max-cost", type=float, dest="max_cost", help="Max cost per 1K tokens (USD)")
    c.add_argument("-v", "--verbose", action="store_true", help="Show routing metadata")

    # serve
    s = sub.add_parser("serve", help="Start the proxy server")
    s.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    s.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    s.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # marketplace
    mp = sub.add_parser("marketplace", help="Browse and manage the marketplace catalog")
    mp_sub = mp.add_subparsers(dest="mp_command", help="Marketplace sub-commands")

    mp_list = mp_sub.add_parser("list", help="List catalog items")
    mp_list.add_argument(
        "--kind",
        choices=["agent", "skill", "combo", "template"],
        help="Filter by item kind",
    )
    mp_list.add_argument(
        "--provider",
        choices=["claude", "copilot", "cursor", "openai", "gemini", "grok", "universal"],
        help="Filter by provider",
    )

    mp_install = mp_sub.add_parser("install", help="Install a marketplace item")
    mp_install.add_argument("item_id", help="Item ID (kebab-case)")

    mp_uninstall = mp_sub.add_parser("uninstall", help="Uninstall a marketplace item")
    mp_uninstall.add_argument("item_id", help="Item ID (kebab-case)")

    mp_info = mp_sub.add_parser("info", help="Show details about an item")
    mp_info.add_argument("item_id", help="Item ID (kebab-case)")

    mp_search = mp_sub.add_parser("search", help="Search the catalog")
    mp_search.add_argument("query", help="Search query string")

    return parser


async def _main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "providers": cmd_providers,
        "models": cmd_models,
        "usage": cmd_usage,
        "cost": cmd_cost,
        "chat": cmd_chat,
        "serve": cmd_serve,
        "marketplace": cmd_marketplace,
    }

    handler = commands.get(args.command)
    if handler:
        await handler(args)
    else:
        parser.print_help()


def main() -> None:
    """Entry point for `cybersec-proxy` script."""
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)


if __name__ == "__main__":
    main()

