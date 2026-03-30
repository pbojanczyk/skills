# Changelog

## 1.2.2 (2026-03-28)

### Documentation
- Declared required env vars (`TODO_DB_*`) in SKILL.md frontmatter and description
- Added explicit warnings for `migrate --action import-delete` (destructive) and cross-agent access (no enforcement, logged only)

## 1.2.1 (2026-03-27)

### Security
- Removed SysClaw reporting integration (was reading `.env` files and executing scripts outside the skill directory)
- Added explicit `ALLOWED_COLUMNS` allowlist to `cmd_edit()` SQL construction

## 1.2.0 (2026-03-17)

### New Features
- **`list --all-agents`**: Show todos from all agents, grouped by owner. Each agent section labeled with 🤖 prefix. Works with `--compact`, `--json`, and all filters.
- **`transfer` command**: Move a todo to another agent. Usage: `transfer <id> --from-agent X --to-agent Y [--to-list Z]`. Creates target list if needed. Cross-agent transfers logged to `todo_access_log`.
- `owner_agent` field added to JSON output when using `--json`.

### Changed
- `--agent` flag on `list` command is now optional (either `--agent` or `--all-agents` required).

## 1.1.0 (2026-03-17)

### Security
- Added `.clawhubignore` to prevent `.env` from being published
- Added `.env.example` with placeholder values
- Added path validation to `migrate` command (restricts to workspace directory)

### Reliability
- Added connection retry logic (3 attempts with exponential backoff: 1s/2s/4s)
- Added `connect_timeout=10` to database connections
- Fixed double-close bug in `cmd_edit` category branch

### Error Handling
- All `ERROR:` messages now go to `stderr` instead of `stdout`

### Documentation
- Added Prerequisites section to SKILL.md (psycopg2-binary, Python 3.7+, PostgreSQL)
- Clarified skill name as "ClawList — Todo Skill"

## 1.0.0 (2026-03-17)

- Initial release
- Full CRUD for todos with lists, categories, priorities, due dates
- Per-agent ownership with cross-agent access logging
- Multiple output modes (default, compact, JSON)
- Migration support from existing task files
