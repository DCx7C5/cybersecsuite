# CyberSecSuite v0.1

A cybersecurity forensics suite with A2A agent orchestration, MCP server support, threat intelligence, and artifact signing capabilities.

## Features

- Forensic analysis framework
- Multi-provider AI proxy routing with 13 strategies
- **QoL output controls** — 8 toggles + 5 presets for cost/compliance optimization
- Cryptographic signing (Ed25519) and hashing (BLAKE2b)
- A2A agent networking
- MCP server integration (87 tools)

## Documentation

- **[Full Docs](docs/README.md)** — Complete reference for all features, architecture, API, and deployment
- **[QoL Guide](docs/features/qol.md)** — Quality of Life output controls: toggles, presets, use cases, and API
- **[Architecture Overview](docs/architecture/overview.md)** — 7-layer system design, QoL flow, components
- **[API Reference](docs/api/http-endpoints.md)** — All HTTP/SSE endpoints including QoL controls

## Installation

```bash
uv sync
```

## Development

```bash
uv sync --group dev
```

## Running Tests

```bash
uv run pytest tests/
```

## License

Proprietary - CyberSecSuite
