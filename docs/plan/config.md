# Config

- In `chitty.toml` at the repo root (written by `chitty init`) or `[tool.chitty]`
  in `pyproject.toml`. Both is an error.
- Unknown keys warn and are ignored.
- New settings are optional, and their defaults generally keep existing
  behaviour, so configs never need migrating. A missing `workflow` defaults to
  the runner for unversioned, unparsable, or versions at most `0.5.0` (with
  trailing zero parts ignored); later versions default to tickets-only. Release
  `0.5.0` upgraded existing runner repositories before init could record an
  explicit workflow, so it belongs on the runner side of the boundary. This
  makes tickets-only Chitty the default for new setups without changing
  existing runner setups.
- Settings with no safe default (`setup`, `check`, `agent_command`) fail where
  `chitty run` needs them.

```toml
format = 1
default_context = "tasks"
autocommit = false # required; true commits each write
# project = "name" # registered name; `chitty run` needs it, `init` derives it
# main_branch = "main" # init writes it only for a new repo on another branch
chitty_version = "0.1.2" # written by init; warns when setup is stale
# workflow = "tickets" # or "runner"; absent resolves from chitty_version
review = true # done only through review → done; default follows workflow
# autoformat = "taidy format" # run on each written task file
# setup = "make install" # run in each ticket worktree before the agent
# check = "make check" # validates the worktree before the agent; also on landing unless landing_check is set
# landing_check = "sh scripts/check_linux.sh" # replaces check on landing only
# agent_command = "pi -p {prompt}" # pass the role guide as one argument
# error_reporter = "sump capture chitty --message {message} --context-json {context}"
# agent_timeout = 7200 # seconds; 0 is no limit
# command_timeout = 3600 # seconds per setup or check invocation; 0 is no limit
# work_model = "provider/model" # when the agent command names no model
# review_model = "provider/model"
# rebase_model = "provider/model" # default for rebase sessions when the command has no model
# job_order = ["review", "doing", "todo"] # statuses `next`/`run` pick, in order
# priorities = ["high", "medium", "", "low"] # highest first; "" places tickets with no priority
archive = "move" # or "delete"
# list_width = 100 # titles fit the smaller of this and terminal width when stdout is a terminal
# protected_paths = ["src/chitty/__init__.py"] # files only main may change

[contexts.tasks]
prefix = "TASK"

[contexts.human]
prefix = "HUMAN"
review = false # overrides the repository default

[contexts.backlog]
prefix = "BACKLOG"
random_ids = true # eight-digit random IDs, so branches cannot collide

[agent_commands]
# name = "command" # chosen for one run with `chitty run --agent NAME`
```

Commands are split like a shell (no shell runs them) and placeholders are
substituted per word. `rebase_model` optionally supplies `--model` for rebase
sessions; when unset, the agent command's model is left unchanged.
`command_timeout` applies separately to setup, pre-agent check and landing
validation commands. Timeouts follow the existing setup, check and landing
failure routing; a check failure may still allow an unfinished work session.

## Contexts

- Directory `chitty/<name>/`; not configurable.
- A context's `review` overrides the repository's; unset inherits it.
- `chitty init` gives new `human` contexts `review = false`.
- `chitty init` adds a `backlog` context after the last context table. It
  skips this when a `backlog` context or `BACKLOG` prefix exists, when contexts
  have no table header to follow, or when the result would not validate.
- Contexts are local to a repository. Send work elsewhere with
  `chitty suggest PROJECT TITLE`; the receiver runs `chitty inbox --pull`.
  `PROJECT` is a registered name; it is a path only if it contains `/`, is `.`,
  or starts with `~` or `.`.

## Review loop limit

- The third `review → doing` since the ticket was last `blocked` becomes
  `review → blocked`, owner `human`, with a note giving the count.
- Unblocking resets the count. The limit is `REVIEW_FAILURE_LIMIT` in
  `store.py`, not a setting.

## Writes

- Each write runs `fix`, then `autoformat`, then `autocommit`. Unresolved fixes
  stop the last two.
- `archive = "delete"` deletes done files and removes their IDs from other
  tickets' `depends_on`. ID allocation then reads Git deletions, including
  uncommitted ones, and fails on shallow or missing history.
