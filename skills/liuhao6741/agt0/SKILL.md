---
name: agt0
description: Local-first agent storage — SQLite database, virtual filesystem, and memory in one .db file. Use when persisting agent state, querying CSV/JSONL/logs with SQL, or using fs_read/fs_write via the agt0 CLI or Node API.
---

# agt0 — Agent Storage Skill

> **One file. All your agent needs.**
> Local-first database + filesystem + memory in a single SQLite file.

---

## Setup

```bash
npm install -g @seekcontext/agt0
agt0 init <dbname>
agt0 use <dbname>          # set as default
```

---

## Essential Patterns

### SQL

```bash
agt0 sql -q "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT)"
agt0 sql -q "INSERT INTO tasks (title, status) VALUES ('Build API', 'doing')"
agt0 sql -q "SELECT * FROM tasks WHERE status = 'doing'"
agt0 sql -f schema.sql
```

### Files (CLI)

```bash
agt0 fs put ./data.csv <db>:/data/data.csv       # upload
agt0 fs put -r ./src <db>:/src                    # upload directory
agt0 fs cat <db>:/data/data.csv                   # read
agt0 fs ls <db>:/data/                            # list
agt0 fs get <db>:/data/data.csv ./local.csv       # download
agt0 fs rm <db>:/data/old.csv                     # delete
```

### Files (SQL)

```sql
SELECT fs_write('/memory/context.md', 'User prefers dark mode');
SELECT fs_read('/memory/context.md');
SELECT fs_append('/logs/session.log', 'Step completed' || char(10));
SELECT fs_exists('/config.json');
SELECT fs_size('/config.json');
```

### Query files as tables

```sql
-- CSV (each row as JSON in _data)
SELECT json_extract(_data, '$.name') AS name
FROM fs_csv('/data/users.csv')
WHERE json_extract(_data, '$.role') = 'admin';

-- JSONL logs
SELECT json_extract(line, '$.level') AS level, COUNT(*)
FROM fs_jsonl('/logs/app.jsonl')
GROUP BY level;

-- Text grep
SELECT _path, _line_number, line
FROM fs_text('/src/**/*.ts')
WHERE line LIKE '%TODO%';

-- Directory listing
SELECT path, type, size FROM fs_list('/data/');
```

### CLI auto-expansion

In `agt0 sql`, `fs_csv`/`fs_tsv`/`fs_jsonl` with a single file path are automatically expanded so `SELECT *` returns real column names (no `json_extract` needed):

```sql
SELECT * FROM fs_csv('/data/users.csv') WHERE role = 'admin';
```

CSV/TSV values are **strings**. For numeric comparison use `CAST`: `WHERE CAST(id AS INTEGER) > 5`.

Glob paths are not expanded — use `json_extract` or `csv_expand`.

### Virtual table modules

For repeated queries on one file, create a virtual table:

```sql
CREATE VIRTUAL TABLE users USING csv_expand('/data/users.csv');
SELECT name, email FROM users WHERE role = 'admin';
```

Modules: `csv_expand`, `tsv_expand`, `jsonl_expand`. Single file only (no globs). Schema fixed at creation — `DROP` and recreate if file changes.

### Import file data into tables

```sql
INSERT INTO users (name, email)
SELECT DISTINCT
  json_extract(_data, '$.name'),
  json_extract(_data, '$.email')
FROM fs_csv('/data/users.csv')
WHERE json_extract(_data, '$.email') IS NOT NULL;
```

---

## SQL Function Reference

### Scalar

| Function | Returns | Description |
|---|---|---|
| `fs_read(path)` | TEXT | Read file |
| `fs_write(path, content)` | INTEGER | Write file (bytes written) |
| `fs_append(path, data)` | INTEGER | Append to file |
| `fs_exists(path)` | INTEGER | 1 if exists |
| `fs_size(path)` | INTEGER | File size (bytes) |
| `fs_mtime(path)` | TEXT | Last modified (ISO 8601) |
| `fs_remove(path [, recursive])` | INTEGER | Delete |
| `fs_mkdir(path [, recursive])` | INTEGER | Create directory |
| `fs_truncate(path, size)` | INTEGER | Truncate to size |
| `fs_read_at(path, offset, len)` | TEXT | Read byte range |
| `fs_write_at(path, offset, data)` | INTEGER | Write at offset |

### Table-Valued

| Function | Columns | Description |
|---|---|---|
| `fs_list(dir)` | path, type, size, mode, mtime | Directory listing |
| `fs_text(path [, opts])` | _line_number, line, _path | Text lines |
| `fs_csv(path [, opts])` | _line_number, _data, _path | CSV rows (JSON) |
| `fs_tsv(path [, opts])` | _line_number, _data, _path | TSV rows (JSON) |
| `fs_jsonl(path [, opts])` | _line_number, line, _path | JSONL lines |

**Globs:** `*` = one segment, `**` = any depth, `?` = one char.

**Options** (JSON string, 2nd arg): `exclude`, `strict`, `delimiter`, `header`.

---

## Database Management

```bash
agt0 list                                # list databases
agt0 inspect <db>                        # overview
agt0 inspect <db> tables                 # table list
agt0 inspect <db> schema                 # CREATE statements
agt0 dump <db> -o backup.sql             # export
agt0 seed <db> schema.sql                # run SQL file
agt0 delete <db> --yes                   # delete
agt0 branch create <db> --name staging   # branch (copy)
agt0 branch list <db>
agt0 branch delete <db> --name staging
```

---

## Storage

```
~/.agt0/
├── config.json
└── databases/
    ├── myapp.db             # tables + files + memory
    └── myapp-staging.db     # branch
```

Override with `AGT0_HOME` env var.

---

## Critical Rules

- All data is **local**. No network, no API keys.
- Each database is a **single `.db` file**. Copy to back up or share.
- The `_fs` table is internal — **never drop it**.
- CSV/TSV rows are JSON in `_data`. Values are **strings**. Use `CAST` for numeric operations.
- JSONL rows are in `line` — values keep their original JSON types.
- Glob `*` matches one segment. Use `**` to cross directories.
- REPL dot commands (`.help`) and FS shell commands (`ls`, `cd`) are **different** interfaces.
