# Layout

```
repo/
  chitty.toml
  chitty/
    tasks/                 default context
      TASK-2--add-search.md
      archive/
        TASK-1--bootstrap.md
    human/
      HUMAN-1--rotate-prod-password.md
    backlog/
      BACKLOG-48213907--idea.md
```

- `chitty/` is the root; each context is a subdirectory, with done tickets in
  `<context>/archive/`. Nothing else lives under `chitty/`.
- A missing context directory is an empty context, created on first write.
  `init` creates only `chitty/tasks/`. Git does not track empty directories, so
  a fresh clone may have none.
- Root discovery (CLI and MCP): `CHITTY_ROOT` if set, else the nearest parent
  directory with `chitty.toml` or a `[tool.chitty]` table in `pyproject.toml`.
  Both in one directory is an error; neither found is an error.
