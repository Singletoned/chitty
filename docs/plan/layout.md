# Layout

```
repo/
  chitty.toml
  chitty/
    tasks/                 default context
      TASK-2--add-search.md
      TASK-3--fix-login.md
      archive/
        TASK-1--bootstrap.md
    human/                 another context
      HUMAN-1--rotate-prod-password.md
```

`chitty/` is the backlog root; each context is a subdirectory. Archived
tasks move to `<context>/archive/`. Nothing else lives under `chitty/`.

A missing context directory is an empty context; it is created on first
write. `init` creates `chitty/tasks/` only; `chitty/human/` appears the first
time something is added to it. (Git doesn't track empty directories, so a
freshly cloned repo may have none of them.)

Root discovery (CLI and MCP alike): `CHITTY_ROOT` if set, otherwise walk up
from the current directory to the first directory containing `chitty.toml` or a
`[tool.chitty]` table in `pyproject.toml`. A repo cannot define both sources;
that ambiguity is an error. Error if neither finds one.
