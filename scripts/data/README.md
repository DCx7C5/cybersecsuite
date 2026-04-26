# Data Processing Tools

Utilities for managing and maintaining data files across the project.

## Scripts

### `fix_skills.py`
Canonicalize and validate skill files for consistency.

**Usage:**
```bash
python scripts/data/fix_skills.py [options]
```

**Options:**
- `--dir <path>` — Directory to scan (default: templates/skills/)
- `--validate` — Validate without making changes
- `--fix` — Apply corrections automatically
- `--report <file>` — Save validation report to file
- `--verbose` — Show detailed processing steps

**Validations:**
- Skill file naming conventions (kebab-case)
- YAML/JSON schema validation
- Required metadata fields
- Character encoding (UTF-8)
- File size limits

**Corrections:**
- Standardize metadata format
- Fix encoding issues
- Normalize field order
- Update category tags
- Add missing descriptions

**Example:**
```bash
python scripts/data/fix_skills.py --dir templates/skills/ --validate
# Found 1,624 skills
# ✓ 1,620 valid
# ⚠ 4 warnings
# ✗ 0 errors

python scripts/data/fix_skills.py --dir templates/skills/ --fix
# Fixed 4 skill files
# All skills now valid
```

## When to Use

- After bulk skill imports
- Data quality checks
- Before skill migration
- Marketplace synchronization
- Legacy data cleanup

## Integration

Used in:
- Phase 9 (Skills Migration) — Pre-migration validation
- Phase 8 (Skills Cleanup) — Bulk data fixes
- CI/CD linting stage

## Output Formats

- **Validation Mode:** Summary + warnings/errors
- **Report Mode:** Detailed JSON report with fixes suggested
- **Verbose Mode:** Line-by-line processing log

## See Also

- `scripts/deploy/` — Deployment tools
- `scripts/test/` — Testing tools
- `scripts/dev/` — Developer tools
