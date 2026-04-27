---
apply: by file patterns
patterns: *.py
---

### Python Rules
- `uv` only (never `pip` or `poetry`)
- Only and always Asynchronous Code
- Every new or edited Python file has to be linted with `ruff` and pass with zero errors; run `uv run ruff check <file>` to verify
