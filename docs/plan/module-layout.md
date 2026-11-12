# Module layout

```
src/chitty/
  __init__.py
  model.py       Task, Frontmatter, Criterion — parse/validate/serialise ONE file
  ids.py         ID and filename parsing, slugs, next number, shorthand
  config.py      RepoConfig, UserContexts — load + validate TOML
  actor.py       stable actor names from harness session identities
  store.py       Context, find/list/read/write/move/archive
  check.py       cross-file validation: parse errors, duplicate IDs,
                 dangling or self depends_on
  errors.py      ChittyError, the base of every user-facing error
  git.py         optional autocommit
  run.py         Pi subprocess runner for `chitty run`
  cli.py         click commands; thin, calls store/model, prints
  mcp.py         tool definitions wrapping the same functions as cli.py
                 (mcp ≥ 2: MCPServer, not FastMCP)
  guide.md       the AGENTS.md block, as package data
  roles/         work, review, and planning instructions, as package data
```

`cli.py` and `mcp.py` contain no logic; both call the same functions in
`store.py`/`model.py` so behaviour cannot diverge. Actor identity comes from
`CHITTY_ACTOR` or a supported harness session variable. Chitty's Pi extension
copies the session ID into `CHITTY_PI_SESSION_ID` at session start, which takes
precedence over Pi's shell-only variable so descendants retain their parent's
identity. context-mode's server starts at `before_agent_start`, after that,
so its commands inherit the variable. Only a server started before
`session_start` needs the `CHITTY_ACTOR` workaround.
