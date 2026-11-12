# Config

Repository config is either `chitty.toml` at repo root (`chitty init` writes it)
or a `[tool.chitty]` table in `pyproject.toml`; defining both is an error. Unknown
configuration keys are ignored with a warning.

Settings are optional, and their defaults keep existing behaviour, so no
config needs migrating (decided with the human, 2026-11-06). Settings with no
safe existing behaviour, such as `setup` and `agent_command`, fail loudly where
`chitty run` uses them.

```toml
format = 1
default_context = "tasks"
chitty_version = "0.1.2" # written by init; warns when setup is stale
autocommit = false # if true, commit each write; `chitty init --autocommit` enables it and commits setup
review = true # require review before done
# autoformat = "taidy format" # run on every written task file
# setup = "make install" # run in every ticket worktree before the agent starts
# check = "make check" # validate the ticket worktree before the agent starts
# agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"
# work_model = "provider/model" # default for work when the agent command has no model
# review_model = "provider/model" # default for review when the agent command has no model
# job_order = ["review", "doing", "todo"] # statuses selected by `next`/`run`, in pick order
# `{prompt}` may be used as one argument containing `chitty guide` output.
archive = "move" # or "delete"; retain completed files or delete them
# list_width = 100 # columns `chitty list` rows fit in

[contexts.tasks]
prefix = "TASK"

[contexts.human]
prefix = "HUMAN"
review = false # overrides the repository default

[contexts.backlog]
prefix = "BACKLOG"
random_ids = true # random eight-digit numbers instead of sequential ones

[agent_commands]
# Other parsed agent commands, selected for one run with `chitty run --agent NAME`.
```

Context directory is `chitty/<name>/`. Not configurable. `review` defaults to
`true`; with it enabled, only `review → done` can complete a task. A context
can set `review` to override the repository default; an absent context setting
inherits it. New `human` contexts disable review so people can close their own
tasks directly.

`chitty init` adds the `backlog` context to an existing repository, as a
table after the last `[contexts.*]` (or `[tool.chitty.contexts.*]`) table. It
leaves the file alone when a `backlog` context or a `BACKLOG` prefix already
exists, when contexts have no table header to follow (dotted keys or inline
tables), or when the result would not validate. An older Chitty refuses a
context with `random_ids`; `chitty_version` already says it needs upgrading.

Agents reviewing each other's work can fail a task back and forth without
converging. The third `review → doing` since the task was last `blocked` is
applied as `review → blocked` with owner `human` and a note giving the count,
alongside the reviewer's own note. Unblocking starts the count again. The
limit is `REVIEW_FAILURE_LIMIT` in `store.py`, not configuration, until a
repository needs a different one.

When set, `autoformat` is parsed without a shell and run on existing files
written by each operation. The order is `fix`, `autoformat`, then `autocommit`;
unresolved fixes prevent the latter two steps. `archive = "move"` is the
standard retention policy. With `archive = "delete"`, archive deletes done
files and strips exact `depends_on` entries elsewhere; ID allocation reads Git
deletions (including uncommitted ones), and fails rather than guessing if the
repository history is shallow or unavailable.

Contexts are repository-local. To send a task to another repository, use
`chitty suggest PROJECT TITLE`; the receiving repository imports its machine-local
inbox with `chitty inbox --pull`. This avoids writing another repository's worktree.
`PROJECT` is a registered project name, which always wins; it is read as a
path only when it contains `/`, is `.`, or starts with `~` or `.`, because
every repository has a `chitty/` folder that a bare name would otherwise hit.
