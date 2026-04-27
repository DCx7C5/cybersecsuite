"""
AI Proxy — multi-provider LLM router with format translation, rate limiting,
cost tracking, and Playwright-based browser automation.

Imports are lazy — provider registry is loaded on first access, not at
package import time. Use specific submodule imports for explicit control.
"""
# Re-exports are deferred to avoid triggering provider loading on import.
# Use: from src.registries.providers import get_all_providers
# Or:  from ai_proxy.routing.combo import smart_route
