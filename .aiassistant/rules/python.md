---
apply: by file patterns
patterns: *.py
---

### Python Rules
- `uv` only (never `pip` or `poetry`)
- Only and always Asynchronous Code
- Every new or edited Python file has to be linted with `ruff` and pass with zero errors; run `uv run ruff check <file>` to verify
- do not work with `global`
- `from __future__ import annotations` is deprecated and not necessary anymore
