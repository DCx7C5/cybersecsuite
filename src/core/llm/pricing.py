"""Anthropic token pricing — updated 2026-04.

Cost is computed from published per-million-token rates.
Update `_PRICES` and `PRICING_LAST_UPDATED` quarterly.
"""
from decimal import Decimal

PRICING_LAST_UPDATED = "2026-04-01"

# (input_per_mtok, output_per_mtok, cache_write_per_mtok, cache_read_per_mtok)
_PRICES: dict[str, tuple[Decimal, Decimal, Decimal, Decimal]] = {
    "claude-opus-4-5":               (Decimal("15.00"), Decimal("75.00"), Decimal("18.75"), Decimal("1.50")),
    "claude-opus-4":                  (Decimal("15.00"), Decimal("75.00"), Decimal("18.75"), Decimal("1.50")),
    "claude-sonnet-4-5":              (Decimal("3.00"),  Decimal("15.00"), Decimal("3.75"),  Decimal("0.30")),
    "claude-sonnet-4":                (Decimal("3.00"),  Decimal("15.00"), Decimal("3.75"),  Decimal("0.30")),
    "claude-haiku-4-5":               (Decimal("0.80"),  Decimal("4.00"),  Decimal("1.00"),  Decimal("0.08")),
    "claude-haiku-4":                 (Decimal("0.80"),  Decimal("4.00"),  Decimal("1.00"),  Decimal("0.08")),
    "claude-3-5-sonnet-20241022":     (Decimal("3.00"),  Decimal("15.00"), Decimal("3.75"),  Decimal("0.30")),
    "claude-3-5-sonnet-20240620":     (Decimal("3.00"),  Decimal("15.00"), Decimal("3.75"),  Decimal("0.30")),
    "claude-3-5-haiku-20241022":      (Decimal("0.80"),  Decimal("4.00"),  Decimal("1.00"),  Decimal("0.08")),
    "claude-3-haiku-20240307":        (Decimal("0.25"),  Decimal("1.25"),  Decimal("0.30"),  Decimal("0.03")),
    "claude-3-opus-20240229":         (Decimal("15.00"), Decimal("75.00"), Decimal("18.75"), Decimal("1.50")),
    "claude-3-sonnet-20240229":       (Decimal("3.00"),  Decimal("15.00"), Decimal("3.75"),  Decimal("0.30")),
}

# Fallback for unknown models (sonnet-class pricing)
_DEFAULT_PRICE: tuple[Decimal, Decimal, Decimal, Decimal] = (
    Decimal("3.00"), Decimal("15.00"), Decimal("3.75"), Decimal("0.30")
)

_MTOK = Decimal("1_000_000")


def cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_write_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> Decimal:
    """Compute cost in USD for one Anthropic API call."""
    inp, out, cw, cr = _PRICES.get(model, _DEFAULT_PRICE)
    return (
        inp * Decimal(input_tokens)        / _MTOK
        + out * Decimal(output_tokens)     / _MTOK
        + cw  * Decimal(cache_write_tokens)/ _MTOK
        + cr  * Decimal(cache_read_tokens) / _MTOK
    )


def known_models() -> list[str]:
    """Return list of models with known pricing."""
    return list(_PRICES.keys())
