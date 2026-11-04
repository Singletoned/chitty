# Chitty

Markdown-native task tracker for repos worked on by humans and coding agents.
Put in a chitty; an agent (or you) picks it up; the file is the record.

Each task is one markdown file with YAML frontmatter under
`chitty/<context>/`, e.g. `chitty/tasks/TASK-12--add-search.md`. The files are
the only state: no database, no index. The tool only ever changes the lines
it means to, so prettier and mdformat leave its output alone and diffs stay
small. See `PLAN.md` for the full design.

## Install

```sh
uv tool install chitty            # CLI
uv tool install 'chitty[mcp]'     # CLI plus `chitty mcp`
uvx chitty --help                 # run without installing
```

To develop Chitty itself, use `make install` in its clone. Each checkout,
including a Git worktree, keeps its disposable virtual environment in `.venv`;
run `make install` after creating a worktree before using its development
commands. Use `uv run chitty` to run a worktree's own code. Do not export
`VIRTUAL_ENV` or `UV_PROJECT_ENVIRONMENT` from `.envrc`: direnv passes them down
to worktrees, where `uv` would repoint a shared install at the worktree.

On a machine used to develop Chitty, install the global `chitty` as an editable
install of the main checkout, which only receives reviewed merges:

```sh
uv tool install --force --editable '/path/to/chitty[mcp]'
```

Every repository on that machine then runs `main`, so a broken `main` breaks them
all. Editable installs do not pick up new dependencies: re-run the command after
a merge that changes them.

## Use

```sh
chitty init                       # create/upgrade config and register its machine-local project inbox
chitty init --autocommit          # enable autocommit and commit the clean setup change
chitty import backlog-md          # convert a reviewed legacy backlog/ directory
chitty suggest other "Improve docs" -d "Explain setup."  # machine-local inbox
chitty inbox                      # list this repo's waiting inbox suggestions
chitty inbox --pull               # print your actor name and collect them as backlog tasks
chitty whoami                     # print your stable actor name
# `add -c` names only a context in this repository; use `suggest` across projects.
chitty add "Add search" -d "Search titles and bodies." \
    --ac "Matches title" --ac "Case-insensitive" -l cli \
    --note "Useful context, repeatable."
chitty list
chitty next                       # print the next `work ID` or `review ID` action
while chitty run; do :; done      # ask Pi to complete actions until no progress
chitty show 1                     # bare numbers mean the default context
chitty edit 1 -s doing --plan "Use casefold()." --check 1
chitty edit 1 -s review
chitty edit 1 -s done --note "Reviewed: ready to merge."
chitty edit 1 --note "Safari needs a polyfill."
chitty edit 1 -s blocked --note "Awaiting a product decision."
chitty add "Refine sync idea" -s backlog  # stores a default refinement note
chitty add "Rotate prod password" -c human -d "Needs a person."
chitty move 1 human               # new ID there; references are rewritten
chitty archive HUMAN-1
chitty check                      # validate everything; non-zero on problems
chitty fix                        # repair safe problems; fail if any remain
chitty archive                     # process every completed task before a merge request
chitty guide                      # instructions for coding agents
```

Every command takes `--json`. `chitty --help` and `chitty <command> --help`
are the reference. Plain `chitty list` shows non-archived `todo`, `doing`,
`blocked`, and `review` tasks across every context; repeat `-c` or `-s` to filter,
including backlog and done tickets. Review is required before `done` by default.
A context can set `review = false` to override that setting; generated `human`
contexts do this so people can close their own tasks directly. The third failed review (`review → doing`) since a task was last blocked sets it
`blocked` with owner `human` instead, so agents stop bouncing it. Use `--parent TASK-1` to show a parent's direct children.
`--all` includes every status but never archive folders.
`chitty next` chooses a `review` ticket before a `doing` or `todo` ticket,
then uses priority and task ID across all non-human contexts. Its `--json`
output is `{"mode": "work"|"review", "id": "TASK-N"}`. `chitty run` requires
`autocommit = true` and `setup` (for example, `setup = "make install"`): it
creates or reuses the ticket worktree, runs setup there, claims a `todo` ticket,
and invokes Pi from that worktree. Pass Pi options with `chitty run -- --model
MODEL`. It succeeds only when Pi commits a status change, so `while chitty run;
do :; done` stops when no action remains or a session makes no progress. Empty lists explain their active filters on stderr while JSON stdout remains
`[]`. `chitty import backlog-md` refuses non-empty contexts, reports
mappings. It refuses to run unless the Git working tree is clean, untracked
files included, and removes the converted files in its import commit; use
`--keep-source` to retain them. Each task has a tool-managed trailing
`## History` that records its creation and status transitions. Finished tasks can include a `## Summary` handoff via
`chitty edit ID --summary TEXT`. To inspect or restore an archived task, work
with its file directly.

Enable tab completion by adding one of these lines to your shell startup file:

```sh
# bash
source <(_CHITTY_COMPLETE=bash_source chitty)
# zsh
eval "$(_CHITTY_COMPLETE=zsh_source chitty)"
```

`chitty whoami` derives a stable readable name from `CHITTY_ACTOR` (when set),
or a coding harness session identity: `CLAUDE_CODE_SESSION_ID`, `PI_SESSION_ID`,
`CODEX_THREAD_ID`, or `CODEX_SESSION_ID`. `CHITTY_ACTOR` is for people and other
tools. Chitty's Pi extension records Pi's session ID in `CHITTY_PI_SESSION_ID`
at session start, so shell commands, `pi.exec`, and subagents share the parent
actor name. Reload or restart Pi after `chitty init` installs or updates the
extension. context-mode starts its server at the first agent turn, after the
variable is set, so its `ctx_execute` commands share the name too. A server
started before `session_start` cannot receive it; start Pi with
`CHITTY_ACTOR=<name>` if one needs the same identity.

Set `autoformat = "mdformat"` in repository config to run a formatter on each
written task file before any autocommit. Set `setup` to the command that prepares
each ticket worktree before Pi starts; it is parsed without a shell. `chitty init --autocommit` enables
`autocommit = true` and commits only the repository setup files it changed
(`chitty.toml` or `pyproject.toml`, `.gitignore`, `AGENTS.md`, and `CLAUDE.md`); it refuses a
dirty Git working tree. Commits for task work should end with
`Task: <ID>` lines using the ticket's own ID (for example, `Task: TASK-12`) so
`git log --grep <ID>` finds a ticket's code. This is a convention, not an
enforced check. Set `archive = "delete"` to delete
completed task files at merge-request time instead of moving them to `archive/`;
it also removes exact `depends_on` entries and requires complete Git history to
avoid reusing IDs. The default, `archive = "move"`, retains task files.

`chitty_version` records the Chitty release that last ran `init`. Reads work with
stale setup, but writes without `autocommit` require `chitty init` first;
with `autocommit = true`, Chitty commits the setup upgrade separately before
writing. `chitty run` also refreshes setup before starting Pi: in a main Git
checkout it commits changed setup files separately, but linked worktrees leave
setup alone. Contexts are configured in `chitty.toml` or `[tool.chitty]` in `pyproject.toml`
(not both). To send work to another repository, use `chitty suggest PROJECT`;
the receiving repository imports it with `chitty inbox --pull`. `PROJECT` is a
registered name unless it contains `/`, is `.`, or starts with `~` or `.`; those
path-shaped values resolve a local Chitty repository.

## Migrating from Backlog.md

From a clone of the legacy repository, run `chitty init`, then
`chitty import backlog-md`. Review its report: statuses declared in
`backlog/config.yml` become backlog with one summary per status, unknown statuses
become backlog notes, unsupported headings are demoted into the description, and
non-task files or folders are listed rather than imported. Run `chitty check`,
review and commit the generated tasks. Clean converted source files, including
`backlog/config.yml`, are removed by the import; delete any remaining reported
non-task files or folders when accepted.

## Develop

```sh
make install    # uv sync --all-extras; npm ci (pinned prettier)
make check      # ruff, pyright, unittest
make format
```

## Pi extension

`chitty init` installs the shipped Pi `/chitty` workflow extension into an existing `~/.pi/agent/extensions/` directory. Start work or review with `chitty run`; pass Pi options after `--`, for example `chitty run -- --model MODEL`. Each invocation works only on the selected ticket, continuing until it leaves `todo`/`doing` in work mode or `review` in review mode. `src/chitty/integrations/pi/chitty.ts` is the source of truth: make extension edits in this repository, not in the installed copy. If the installed file differs, `chitty init` fails rather than overwriting possible local work; review it, then replace or remove it before retrying. Restart or reload Pi after installation.
