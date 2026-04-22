# Plan: Fix ruff.lint + Tests + Changelog

**Date:** 2026-04-23  
**Scope:** Fix all remaining issues in `ruff.lint`, fix test collection blocker, add coverage tests, write changelog.

---

## Status

| Code | Count | Status   | Strategy                                                      |
|------|-------|----------|---------------------------------------------------------------|
| F401 | 47    | ✅ DONE  | Removed dead imports; replaced HAS_X probes with `find_spec` |
| E741 | 25    | pending  | Rename ambiguous `l` per-context (see detail table below)     |
| E701 | 17    | pending  | Split `if cond: body` onto two lines                          |
| E702 | 8     | pending  | Split `a; b` onto two lines                                   |
| F821 | 3     | pending  | Add missing import or fix self-referential init               |
| F823 | 1     | pending  | Remove shadowing local variable in `main()`                   |
| E402 | 1     | pending  | Move `import sys` to top in `test_poc_model.py`               |

**Plus:** `tests/test_integrity_checks.py` — still imports `a2a.checks.integrity` (module deleted). Update to `checks.integrity`.

**Total remaining: 55 violations across 32 files.**

---

## F821 / F823 — Runtime Crashes (fix first)

| File | Line | Issue | Fix |
|------|------|-------|-----|
| `network/ids/snort/scripts/agent.py` | 16 | `DAQ_DIR = os.environ.get(..., DAQ_DIR)` — self-referential default | Replace default with literal `"/usr/local/lib/daq"` |
| `intel/feeds/stixfeed/scripts/agent.py` | 204 | `os` used at line 204, `import os` at line 205 | Add `import os` to top-level imports; simplify `__main__` block |
| `malware/ioc/malware/scripts/agent.py` | 101 | `datetime.utcnow()` — `datetime` never imported | Add `from datetime import datetime` at top |
| `soc/siem-soc/correlation-rules/scripts/agent.py` | 216 | `os` module-level import (line 7) shadowed by local `os =` inside `main()` | Remove/rename the local `os` variable |

---

## E402 — Import Order

| File | Line | Fix |
|------|------|-----|
| `tests/test_poc_model.py` | 52 | Move `import sys` to the top of the file with other stdlib imports |

---

## E741 — Ambiguous Variable Name `l` (25 violations, 15 files)

| File | Lines | Rename to |
|------|-------|-----------|
| `compliance/cloud/nerc/scripts/agent.py` | 71, 77 | `ln` (iterates over stdout lines) |
| `crypto/crypto-pki/hashcat/scripts/agent.py` | 106 | `pwd_len` (`l = len(p)`) |
| `crypto/crypto-pki/transparency/certificates/scripts/agent.py` | 58, 198 | `entry` (iterates over lookalike dicts) |
| `identity/mfa/duo/scripts/agent.py` | 88, 89, 94 | `log` (iterates over auth log entries) |
| `malware/c2/covenant/scripts/agent.py` | 81 | `listener` (iterates over listeners list) |
| `malware/c2/havoc/scripts/agent.py` | 103, 112 | `listener` |
| `malware/dynamic/scripts/agent.py` | 19 | `ln` |
| `malware/dynamic/scripts/process.py` | 77, 78, 79 | `ln` |
| `malware/ioc/virustotal/scripts/agent.py` | 115 | `lookup_parser` (subparser var, update `.add_argument` calls too) |
| `malware/reversing/ios/frida/scripts/process.py` | 89 | `ln` |
| `malware/yara/scripts/agent.py` | 157 | `ln` |
| `network/ipv6/scripts/agent.py` | 106, 108 | `ln` |
| `network/wireless/pentest/scripts/agent.py` | 110 | `ln` |
| `osint/shodan/scripts/agent.py` | 102 | `lookup_parser` (subparser var, update `.add_argument` calls too) |
| `web-application/ai/model/scripts/agent.py` | 128 | `ln` (generator expression over lines) |
| `web-application/auth/evilginx/scripts/agent.py` | 138 | `logs_parser` (subparser var, update `.add_argument` calls too) |
| `web-application/broken/scripts/agent.py` | 103 | `lnk` (iterates over links) |

---

## E701 / E702 — Compound Statements (17 + 8 = 25 violations, 4 files)

All four files share the same two patterns:

**Pattern A — semicolons in argparse setup (E702, line ~74–77):**
```python
# before
h = sp.add_parser("hunt"); h.add_argument("--input", "-i", required=True); h.add_argument("--output", "-o", default="...")
# after
h = sp.add_parser("hunt")
h.add_argument("--input", "-i", required=True)
h.add_argument("--output", "-o", default="...")
```

**Pattern B — compound if/else in CLI dispatch (E701, lines ~77–88):**
```python
# before
if args.cmd == "hunt": run_hunt(args.input, args.output)
...
else: p.print_help()
if __name__ == "__main__": main()
# after
if args.cmd == "hunt":
    run_hunt(args.input, args.output)
...
else:
    p.print_help()
if __name__ == "__main__":
    main()
```

**passthehash** also has 5 early-return E701s (lines 26–34):
```python
# before
if eid != "4624": return None
# after
if eid != "4624":
    return None
```

| File | E702 lines | E701 lines |
|------|-----------|-----------|
| `identity/kerberos/kerberoasting/scripts/process.py` | 74 | 77, 81, 83 |
| `identity/ntlm/passthehash/scripts/process.py` | 77 | 26, 28, 30, 32, 34, 80, 86, 88 |
| `identity/serviceaccount/service/scripts/process.py` | 72 | 75, 79, 81 |
| `malware/persistence/registry/scripts/process.py` | 76 | 79, 83, 85 |

---

## Test Collection Blocker

`tests/test_integrity_checks.py:5` imports `from a2a.checks.integrity import ...`  
Module was deleted. Update to `from checks.integrity import ...`

---

## F401 — DONE

All 47 F401 violations resolved. See previous work:
- Dead imports removed from try blocks
- `HAS_X` availability probes replaced with `importlib.util.find_spec(...)`
- Zero `# noqa` comments needed

---

## Phases

1. **Fix test collection blocker** — `test_integrity_checks.py` wrong import path
2. **Fix F821/F823** — 4 files with runtime crashes
3. **Fix E402** — move `import sys` in `test_poc_model.py`
4. **Fix E741** — rename `l` in 15 files (25 violations)
5. **Fix E701/E702** — split compound statements in 4 files (25 violations)
6. **Run `uvx ruff check`** — verify zero errors
7. **Run `make test`** — verify all tests pass
8. **Add coverage tests** — for `checks.integrity`, `crypto`, `a2a` modules
9. **Write changelog** — `docs/changelog/ruff-lint-fix-2026-04-23.md`

---

## Notes
- All files are under `templates/` or `tests/` — outside `src/`, but ruff checks them.
- `templates/` paths above are abbreviated; full path is `templates/skills/<path>`.
- After each phase, re-run `uvx ruff check --select <CODE>` to confirm clean.
