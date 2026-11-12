# Module layout

```
src/chitty/
  model.py           Task, Frontmatter, Criterion: parse, validate, write one file
  ids.py             IDs, filenames, slugs, shorthand
  config.py          RepoConfig: load and validate TOML
  store.py           Repo: find, list, read, write, move, archive; next_action
  selection.py       pure ticket eligibility and ordering for `next`
  check.py           cross-file validation: parse errors, duplicate IDs, bad depends_on
  formatter.py       run the configured task-file formatter
  git.py             Git calls, autocommit
  locks.py           per-ticket run locks
  run.py             `chitty run`
  inbox.py           machine-local suggestion inboxes
  import_backlog.py  pure conversion of one Backlog.md task file
  upgrade.py         advice about newer Chitty releases
  actor.py           stable actor names from harness session IDs
  errors.py          ChittyError, base of every user-facing error
  cli.py             Click commands: thin
  mcp.py             MCP tools (mcp ≥ 2, `MCPServer`): thin
  guide.md           the managed AGENTS.md block, package data
  roles/             per-role guides, package data
  integrations/      agent-specific code: Pi extension (`pi/chitty.ts`), Claude
                     usage hook (`claude/usage.py`)
```

- `cli.py` and `mcp.py` hold no logic; both call `store.py` and `model.py`, so
  they cannot diverge.
- Actor identity comes from `CHITTY_ACTOR`, else a harness session variable
  (`CLAUDE_CODE_SESSION_ID`, `CHITTY_PI_SESSION_ID`, `PI_SESSION_ID`,
  `CODEX_SESSION_ID`). The Pi extension copies Pi's session ID into
  `CHITTY_PI_SESSION_ID` at session start, so descendants keep the parent's
  identity.
