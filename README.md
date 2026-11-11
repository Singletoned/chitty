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

Keep the global `chitty` on the latest PyPI release, as above, so other
repositories run released code. In the Chitty clone itself, `main` is usually
ahead of PyPI, and the global `chitty` would refuse to write. Add this to the
clone's ignored `.envrc`, so a bare `chitty` there, worktrees included, runs the
main checkout's `.venv`:

```sh
PATH_add .venv/bin
```

Adding to `PATH` repoints no `uv` environment, unlike the variables above.

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
chitty run --loop --mode work     # keep working; wait for new tickets when idle
chitty show 1                     # bare numbers mean the default context
chitty edit 1 -s doing --plan "Use casefold()." --check 1
chitty edit 1 -s review
chitty edit 1 -s done --note $'Reviewed: ready to merge.\n1: pass - tests/test_store.py'
chitty edit 1 --note "Safari needs a polyfill."
chitty edit 1 -s blocked --note "Awaiting a product decision."
chitty add "Refine sync idea" -s backlog  # stores a default refinement note
chitty add "Rotate prod password" -c human -d "Needs a person."
chitty move 1 human               # new ID there; references are rewritten
chitty renumber chitty/tasks/TASK-24--old-title.md  # one of two files sharing an ID
chitty archive HUMAN-1
chitty check                      # validate everything; non-zero on problems
chitty fix                        # repair safe problems; fail if any remain
chitty archive                     # process every completed task before a merge request
chitty guide                      # managed `AGENTS.md` instructions for coding agents
chitty guide setup                # help an agent configure `chitty run`
chitty guide work TASK-12         # instructions for one implementation ticket
chitty guide review TASK-12       # instructions for one review ticket
chitty guide plan                 # instructions for writing and refining tickets
```

Every command takes `--json`. `chitty --help` and `chitty <command> --help`
are the reference. `chitty guide` prints the managed `AGENTS.md` block; `chitty init` wraps that
block in strict `chitty:begin` and `chitty:end` markers so only Chitty's text is
replaced. Existing unmarked blocks are migrated on the next init.
`chitty guide setup` prints a repository-independent checklist for configuring
`chitty run` from the main checkout; `chitty guide --help` lists every guide
and shows example commands. `chitty guide work`, `review`, and `plan` print the
focused instructions for those roles from the packaged role files. The short
block in `AGENTS.md` points agents started by hand to their matching role guide.
Work, review and cold-read take an optional ticket ID; setup and planning do not.
Plain `chitty list` shows non-archived `planning`, `cold-read`, `todo`, `doing`,
`blocked`, and `review` tasks across every context; repeat `-c` or `-s` to filter, including backlog and
done tickets. Each row shows the status as a glyph and at most five letters: `💤 bklog`,
`📝 plan`, `🔎 cold`, `📋 todo`, `🔨 doing`, `⛔ blckd`, `👀 revw`, or `✅ done`, then
the priority
as `⬆️` high, `⏺️` medium or `⬇️` low. Titles are cut with `…` so rows fit in
`list_width` columns (100 unless `chitty.toml` sets it). Rows skipped by
`chitty next` carry a glyph in a column before the title: `👤` owned or human,
`🔒` waiting on a dependency, `▶` running, or `⚠️` a broken dependency, whose
message goes to stderr. `--json` gives the full reason as `skipped`. Review is required before `done` by default.
A context can set `review = false` to override that setting; generated `human`
contexts do this so people can close their own tasks directly. A context with
`random_ids = true` numbers new tickets at random from 10000000 to 99999999
instead of sequentially, so tickets raised on different branches do not
collide; `chitty init` adds such a `backlog` context (prefix `BACKLOG`) to new
and existing repositories, unless one or a `BACKLOG` prefix already exists. The third failed review (`review → doing`) since a task was last blocked sets it
`blocked` with owner `human` instead, so agents stop bouncing it. Use `--parent TASK-1` to show a parent's direct children.
`--all` includes every status but never archive folders.
When a merge leaves two files sharing an ID, which `chitty check` reports,
`chitty renumber PATH` gives that one file the next number in its context,
keeping its slug and recording `moved_from`. It refuses a file whose ID is
unique (use `chitty move`). It does not rewrite references, because a
`depends_on` or `parent` naming the shared ID cannot say which file it meant;
it lists each ticket naming the old ID for you to check.
`chitty next` chooses a `review` ticket before a `doing` or `todo` ticket,
then uses priority and task ID across all non-human contexts. Plain selection
skips every owned ticket; `chitty list` uses the same skip rules and reports
ownership, human context, unmet `todo` dependencies, and broken dependency
references. `doing` and `review` tickets ignore dependencies; dependency
completion is judged from the main branch. Use `--owner NAME` to select only that
owner's tickets in any active status.
`human` and empty owner filters are refused. Its `--json`
output is `{"mode": "work"|"review", "id": "TASK-N"}`. `--mode review` chooses
only among `review` tickets and `--mode work` only among `doing` and `todo`, in
the same order. With nothing to choose, `chitty next` and `chitty run` print
`no next ticket` (with the mode, if given) and exit 3, which no other failure
uses. `chitty run --mode MODE` does the same, so
`chitty run --mode review -- --model MODEL` gives reviews their own model. Any
number of workers and reviewers may run at the same time. Each `chitty run`
holds a lock on its ticket until it exits, an exclusive `flock` on
`.git/chitty/run/<ID>.lock` that the kernel releases however the run ends. The
lock file records JSON with the process ID, actor, `work` or `review` mode, and
UTC start time. `chitty show` reports a held ticket as `running: <mode> by
<actor>, process <pid>, since <HH:MM>` (local time), or `running: you (<actor>,
<mode>, process <pid>, since <HH:MM>)` when the actor is this session's
`CHITTY_ACTOR`; `--json` and MCP show give the same answer as `"you"`. `chitty
list` marks it `▶`; `chitty next` and other runs skip it and `--ticket` refuses it
with the holder's process ID. Locks are machine-local. The sessions all update
main checkout during setup and review merges, so a Git lock or
dirty file collision fails loudly; rerun the affected session. `--mode` cannot be
combined with `--ticket`. `chitty run` requires
`autocommit = true`, `setup` (for example, `setup = "make install"`), `check`
(for example, `check = "make check"`), and an `agent_command`, unless `--agent
NAME` selects an entry from `[agent_commands]`. Both commands are parsed
without a shell; it must include `{mode}` and `{id}`, or `{prompt}`.
Chitty replaces placeholders after splitting it;
`{prompt}` contains `chitty guide <mode> <ID>` output as one argument.
`chitty run` creates or reuses the ticket worktree, runs setup there, claims a
`todo` ticket, and invokes
the configured agent from that worktree. The agent uses the `chitty`
executable installed beside the runner's Python interpreter, rather than a
branch-local `chitty`; `pi` and `claude` still come from the global `PATH`.
This behavior is implemented without changing `chitty.toml` on the branch.
Moving a ticket to `review` requires a clean worktree. `chitty check` flags
uncommitted files on the current ticket branch while it is in review; work
branches can remain dirty during development. Before a review `chitty run`
merges the main branch into the ticket branch, then runs setup and check, so
the reviewer sees exactly what would land. Uncommitted files instead block the
ticket for a human immediately, without starting a reviewer. Merge conflicts
still move it back to `doing` with a `Review failed (integration)` note and
count towards the failed-review limit. A passing review lands by fast-forwarding `main` only
after these checks pass; the reviewer should not merge or remove branches or
worktrees. Without `chitty run`, merge `main` into the ticket branch in its
worktree, run the configured checks, and only then fast-forward `main`. In work
mode, a failing check on an already-`doing`
ticket is recorded as `Check failed before this session: ...` and the agent
starts so it can fix the branch. A failing check on a `todo` ticket exits 1
with `check failed before <ID> started: ...`, leaving the ticket unchanged and
starting no agent. Choose a ticket with `chitty run
--ticket ID`; pass agent options with `chitty run -- --model MODEL`. Use
`chitty run --owner NAME` to select that owner's tickets; it cannot be combined
with `--ticket`. It
succeeds only when the agent commits a status change, so
`chitty run --loop --mode work -- --model MODEL` keeps running, waiting 60
seconds between attempts after both successful actions and idle queues. Each
attempt starts a fresh process, so it picks up code landed by the last run. It
stops on any real failure or interruption (Ctrl-C exits 130); `--loop` cannot
be used with `--ticket`. Without `--loop`, `chitty run` still exits 3 on an
idle queue. Each loop pass checks configuration and refreshes setup before
selecting, so a broken configuration exits 1 and stops the loop. Each agent
session appends one JSON line to the machine-local
`$XDG_DATA_HOME/chitty/usage/<project>.jsonl` usage log (or the platform data
directory when `XDG_DATA_HOME` is unset), including the ticket, actor, timing,
statuses, and aggregate Pi token and cost totals by model. These costs are
provider list prices, not negotiated rates or an invoice. Empty lists explain
their active filters on stderr while JSON stdout remains `[]`.
`chitty import backlog-md` refuses non-empty contexts, reports mappings. It refuses to run unless the Git working tree is clean, untracked
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
each ticket worktree before the agent starts; it is parsed without a shell. Set
`agent_command` to the default agent invocation, for example
`"pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"`.
The optional `agent_timeout` is a non-negative integer number of seconds and
defaults to 7200; set it to `0` for no limit. On timeout, `chitty run` stops the
agent and its child processes and exits with an error.
Additional commands go in `[agent_commands]`; `chitty run --agent NAME` uses one
for that run only. An unknown name lists available entries, and the selected
entry is validated like `agent_command`. Optional root-level `work_model` and
`review_model` (or keys directly in `[tool.chitty]` in `pyproject.toml`) set
independent model defaults for unattended runs. Chitty appends `--model MODEL`
only if neither the selected command nor forwarded arguments after `--` already
specify `--model`; an agent receiving a default must accept that option.
Existing model arguments take precedence, without Chitty rewriting them.
Each word expands a leading `~`; `{mode}` and `{id}` become `work` or `review`
and the selected ticket ID. `{prompt}` can replace both placeholders when the
agent accepts Chitty's role instructions as one argument. `chitty init --autocommit`
enables
`autocommit = true` and commits only the repository setup files it changed
(`chitty.toml` or `pyproject.toml`, `.gitignore`, `AGENTS.md`, and `CLAUDE.md`); it refuses a
dirty Git working tree. Commits for task work should end with
`Task: <ID>` lines using the ticket's own ID (for example, `Task: TASK-12`) so
`git log --grep <ID>` finds a ticket's code. This is a convention, not an
enforced check. Set `archive = "delete"` to delete
completed task files at merge-request time instead of moving them to `archive/`;
it also removes exact `depends_on` entries and requires complete Git history to
avoid reusing IDs. The default, `archive = "move"`, retains task files.

`chitty_version` records the Chitty release that last ran `init`. When a newer
release is available, Chitty prints `chitty <version> is out: run uv tool
upgrade chitty` to stderr. The check is skipped for editable installs and
completion requests. Reads work with stale setup, but writes without
`autocommit` require `chitty init` first;
with `autocommit = true`, Chitty commits the setup upgrade separately before
writing. `chitty run` also refreshes setup before starting the agent: in a main Git
checkout it commits changed setup files separately. From a linked worktree it
leaves setup alone, but refuses to run when the main checkout's setup is older
or unrecorded; run `chitty run` from the main checkout instead. Contexts are
configured in `chitty.toml` or `[tool.chitty]` in `pyproject.toml`
(not both). Unknown configuration keys are ignored with a warning. To send work
to another repository, use `chitty suggest PROJECT`;
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

`chitty init` installs the shipped Pi `/chitty` workflow extension into an existing `~/.pi/agent/extensions/` directory. Configure Pi with `agent_command` to start work or review with `chitty run`; pass agent options after `--`, for example `chitty run -- --model MODEL`. Each invocation works only on the selected ticket, continuing until it leaves `todo`/`doing` in work mode or `review` in review mode. `src/chitty/integrations/pi/chitty.ts` is the source of truth: make extension edits in this repository, not in the installed copy. If the installed file differs, `chitty init` fails rather than overwriting possible local work; review it, then replace or remove it before retrying. Restart or reload Pi after installation.
