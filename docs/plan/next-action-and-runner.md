# Next action and runner

## `chitty next`

- Picks one active ticket across all contexts, ordered by:
  - status, from `job_order` (default `review`, `doing`, `todo`); statuses left
    out are never picked;
  - priority: high, then medium or unset, then low;
  - ID.
- Skips:
  - human-context tickets and tickets owned by `human`;
  - `error` tickets, which require explicit repair selection;
  - `todo` tickets with an unmet dependency (`doing` and `review` ignore
    dependencies).
- `chitty list` marks skips: `👤` human or owned, `✍️` untestable,
  `🔗` waiting on a dependency, `⚠️` a broken dependency. It marks `🚧` on
  active chain endpoints that have waiting dependents and no unfinished or
  broken dependency of their own; skip and dependency markers take precedence.
- Prints `work ID` or `review ID`. `--json` and the read-only MCP `next` tool
  give `{mode, id}`.
- `--mode review` allows `review`; `--mode work` allows `doing` and `todo`.
  Repeat to allow several; none allows all. Mode filtering comes before the
  dependency check, so a bad reference in the other mode cannot block this one.
- Nothing to pick: `no next ticket` (or `no next ticket for --mode review or
  work`) on stderr, exit 3, so idle differs from broken (exit 1). Every `todo`
  waiting on a dependency counts as idle. `chitty run` exits 3 the same way.

## `chitty run`

- Before starting, preflight reports every missing required setting in one error;
  it does not run setup, select a ticket, or launch an agent until the error is
  fixed. The configuration looks like this (use the repository's actual
  commands):

  ```toml
  autocommit = true
  setup = "make install"
  check = "make check"
  agent_command = "pi -p {prompt}"
  ```

  `autocommit`, `setup`, and `check` are always required. The default
  `agent_command` is required unless `--agent NAME` selects a command from
  `[agent_commands]`. The error names the config file it checked and includes
  an example for each missing setting.
- At the start of every run, under the landing lock and after pruning stale
  worktree registrations, remove local ticket branches whose tips are contained
  by `main_branch`; this precedes pending landings. A merged branch is kept if
  its ticket exists and is not `done`, its run lock is held, its worktree is dirty
  or has a merge/rebase in progress, it is the main checkout, or worktree/branch
  removal fails. Ignored files do not make the worktree dirty. Emit
  `removed merged branch <b>` or `kept merged branch <b>: <reason>` to stderr.
- A plain run first lands any non-archived `done` ticket that still has a
  branch named for its ID, in ID order. It lands one, then exits 0; the next
  run refreshes setup first. `--ticket` skips this.
- Selection: as `chitty next`, including `--mode`. Plain runs skip owned `todo`
  and `doing` tickets but still take owned `review` tickets. `--owner NAME`
  takes only that agent's tickets, at any active status. `--errors` selects only
  `error` tickets and supplies a repair prompt; it cannot be combined with
  `--ticket`, `--mode`, or `--owner`.
- Refused: `--mode` or `--owner` with `--ticket`, `--owner human`, empty
  `--owner`, and the `--errors` combinations described above.
- Works from any worktree: finds the main checkout, makes or reuses a ticket's
  worktree, claims a `todo` ticket on its branch, then runs `setup` there before
  starting the agent.
- The agent uses the `chitty` beside the runner's Python, not the branch's.
  `pi` and `claude` come from `PATH`. The branch's `chitty.toml` is untouched.

### Agent command

- `{mode}` is `work`, `review`, or `repair` for an error ticket.
- Split like a shell, then placeholders replaced per word.
- `{prompt}` is the `chitty guide <mode> <ID>` output, as one argument.
  Without it the command must have `{mode}` and `{id}`.
- Arguments after `--` go to the agent.
- `work_model`/`review_model`/`rebase_model` add `--model MODEL` for that mode, unless the
  command or forwarded arguments already give `--model`. Chitty has no
  `--model` option of its own.
- Success means the ticket's committed status changed. An error repair must
  finish in `review`, `blocked`, or `error`; the repair prompt explains these
  outcomes.
- Exit 0 with the status unchanged, and the command has `{prompt}`: run again
  with the continuation prompt and `-c` appended, up to `MAX_CONTINUATIONS`
  (5) times, then fail with `was unchanged`. `{mode} {id}` commands are not
  continued.
- `agent_timeout` (default 7200 seconds, `0` no limit) applies per session. On
  expiry: `SIGTERM` the agent and its descendants, `SIGKILL` after
  `AGENT_KILL_GRACE_SECONDS`, print `agent timed out after N seconds`, exit 1.
- `command_timeout` (default 3600 seconds, `0` no limit) applies separately to
  each setup, pre-agent check and landing validation command. Setup and landing
  timeouts use their existing error paths; check timeouts use the usual check
  failure routing, including continuing an unfinished work session.
- If an agent session fails before any commit, restore the selected ticket status,
  leave uncommitted files untouched, and stop the loop with an error.
- The agent stays in the runner's process group and session, so the terminal
  and Ctrl-C work. Never `start_new_session`.

### `--loop`

- Repeats, waiting `RUN_LOOP_PAUSE_SECONDS` (60) after each success or idle
  queue. Each attempt is a fresh `chitty run` process, so code changed by a
  landing is reloaded.
- Takes `--mode`, `--owner`, `--agent` and forwarded arguments; not
  `--ticket`.
- Each attempt checks config and refreshes setup first. Config, setup or agent
  failure stops the loop with exit 1; Ctrl-C with exit 130, no traceback.
- Prints rules to stderr: `chitty run · HH:MM:SS` before each attempt, then
  `finished · next run at …`, `no ticket · next run at …`, or
  `stopped · exit N`.

## Before a review

`main` is the base every ticket branch builds on. The runner rebases the branch
onto `main` whenever it touches it. Ticket files change only on their branch and
rebase like any other file; conflicts go to an agent, not a ticket merge.

`chitty run` prepares the worktree so the reviewer sees what would land:

1. A missing ticket branch and worktree is a runner error: set `error` with a `Runner error (review)` note naming the missing branch and saying no worktree exists; do not change the owner or start an agent.
2. An unfinished merge or rebase is an error for the human; no status change.
3. Uncommitted files (untracked and not ignored included): block for `human`
   with `Review blocked (work): ...`. No reviewer starts.
4. Rebase the branch onto local `main`, with `rerere.enabled=false`. On conflict,
   run one agent session with mode `rebase` and the `chitty guide rebase` prompt
   before starting a separate reviewer. The session must finish the rebase and
   leave the worktree clean. Otherwise abort any remaining rebase and move to
   `doing` with a one-line `Review failed (integration):` note naming the
   conflicts in `main` and the paths, followed by `the rebase session failed:`
   and the session error's first line. No reviewer starts after session failure.
5. A branch that changes the Chitty config (`chitty.toml` or `[tool.chitty]`)
   or the managed block in `AGENTS.md`: move to `doing` with
   `Review failed (work): ...`.
6. Run `setup`, then `check`. Files left uncommitted: block for `human`. Check
   failure: move to `doing` with the last 20 lines, fenced, in
   `Review failed (work)`; no agent, no usage line, exit 0.

- These moves use the run's own actor, so they count towards
  `REVIEW_FAILURE_LIMIT`. Ctrl-C during the rebase aborts it, exit 130.
- Work mode makes or reuses the worktree and claims a `todo` ticket on its
  branch, then runs `setup` and `check`. A non-zero `check` exit
  on a `doing` or `error` ticket appends a `Check failed before this session`
  note pointing to the full output in `.chitty/check.log`, leaves the status
  unchanged, and starts the agent; an `error` ticket's agent is the repair agent.
  A `todo` ticket whose branch changes files outside `chitty/` is treated the
  same way. On a `todo` ticket without work outside `chitty/`, or when the
  `check` command is not found, the ticket moves to `error` with a note (for a
  failed check, pointing to `.chitty/check.log`; for a missing command, naming
  it) and no agent starts.
- Entering `review`, or `review → done`, needs a clean worktree; `blocked` does
  not. `chitty check` reports dirty files on a branch in review.
- Reviewers record a verdict only; they never merge or remove branches or
  worktrees. A manual reviewer checks `git status --short` first and blocks a
  dirty ticket for `human`.

## Landing

On a pass, under the landing lock:

- A short main-checkout lock serializes writes and landing's clean-tree check plus
  fast-forward. Landing takes locks in order: landing lock, then main-checkout
  lock; it does not hold the latter during setup, checks or rebase.
- The main checkout must be on `main_branch` and clean.
- Refused: uncommitted files in the worktree, a changed Chitty config, or a
  changed managed block in `AGENTS.md`, before or after merging.
- Rebase the branch onto `main_branch`, run `setup` and `check`, fast-forward
  `main_branch`, then remove the worktree and branch. If fast-forward loses a
  race and the new commits touch only configured context ticket directories,
  Chitty rebases and retries without rerunning the check, assuming checks do not
  depend on ticket files. Repositories whose check validates tickets (for
  example `chitty check`) or scans `chitty/` for conflict markers (this
  repository's `make check`) do not satisfy that assumption.
- A ticket-scoped setup, check, agent, or landing failure moves the ticket to
  `error`, records the phase, output, and worktree in Notes, and preserves its
  branch and worktree. The exception is the work-mode non-zero `check` exit on
  a `doing` or `error` ticket described under "Before a review": the agent
  starts instead. Failures before a safe ticket handoff leave task state
  unchanged and use `error_reporter` when configured.
- Without `chitty run`: rebase the branch onto `main` in its worktree, run the
  checks, then only fast-forward `main`.

## Agent output log

One file per selected ticket attempt lives in `chitty/run/` under Git's common
directory. Its name includes the ticket ID and UTC timestamp with microseconds.
It contains merged agent stdout and stderr from every session in that attempt,
including rebase and continuation sessions. Setup and check logs are separate.
Once the file is created, the runner closes it and prints `log: <absolute path>`
to stderr when the attempt ends, even on failure.

## Usage log

- One JSON line per run in `$XDG_DATA_HOME/chitty/usage/<project>.jsonl` (or
  the platform data directory): ticket, mode, actor, start, elapsed seconds,
  statuses.
- No token or cost data. Spend by model comes from the agent's session files,
  for Pi via `scripts/pi_tokens.py`.
