---
apply: always
---

### Development Rules
- working directory is `.aiassistant/workdir/`
- all `.md` files use lowercase and hyphen in their file name only
- new plans go to `plans/` in project root
- plans created in working dir of model must be synced with `plans/`
- `mcp` implementation only via SDK 
- single MCP server usage
- no `Co-authored-by:` in commits