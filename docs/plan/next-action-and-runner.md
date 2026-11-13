# Next action and runner

## `chitty next`

- Picks one active ticket across all contexts, ordered by:
  - status, from `job_order` (default `review`, `doing`, `todo`); statuses left
    out are never picked;
  - priority: high, then medium or unset, then low;
  - ID.
- Skips:
  - human-context tickets and tickets owned by `human`;
  - `todo` tickets with an unmet dependency (`doing` and `review` ignore
    dependencies).
- `chitty list` marks skips: `👤` human, `🔒` waiting on a dependency, `⚠️` a
  broken dependency.
- Prints `work ID` or `review ID`. `--json` and the read-only MCP `next` tool
  give `{mode, id}`.
- `--mode review` allows `review`; `--mode work` allows `doing` and `todo`.
  Repeat to allow several; none allows all. Mode filtering comes before the
  dependency check, so a bad reference in the other mode cannot block this one.
- Nothing to pick: `no next ticket` (or `no next ticket for --mode review or
  work`) on stderr, exit 3, so idle differs from broken (exit 1). Every `todo`
  waiting on a dependency counts as idle. `chitty run` exits 3 the same way.

## `chitty run`

- Requires `autocommit = true`, `setup`, and `agent_command` (or
  `--agent NAME` from `[agent_commands]`).
- A plain run first lands any non-archived `done` ticket that still has a
  branch named for its ID, in ID order. It lands one, then exits 0; the next
  run refreshes setup first. `--ticket` skips this.
- Selection: as `chitty next`, including `--mode`. Plain runs skip owned `todo`
  and `doing` tickets but still take owned `review` tickets. `--owner NAME`
  takes only that agent's tickets, at any active status.
- Refused: `--mode` or `--owner` with `--ticket`, `--owner human`, empty
  `--owner`.
- Works from any worktree: finds the main checkout, creates or reuses the
  ticket's worktree, runs `setup` there, then claims a `todo` ticket on its
  branch before starting the agent.
- The agent uses the `chitty` beside the runner's Python, not the branch's.
  `pi` and `claude` come from `PATH`. The branch's `chitty.toml` is untouched.

### Agent command

- Split like a shell, then placeholders replaced per word.
- `{prompt}` is the `chitty guide <mode> <ID>` output, as one argument.
  Without it the command must have `{mode}` and `{id}`.
- Arguments after `--` go to the agent.
- `work_model`/`review_model` add `--model MODEL` for that mode, unless the
  command or forwarded arguments already give `--model`. Chitty has no
  `--model` option of its own.
- Success means the ticket's committed status changed.
- Exit 0 with the status unchanged, and the command has `{prompt}`: run again
  with the continuation prompt and `-c` appended, up to `MAX_CONTINUATIONS`
  (5) times, then fail with `was unchanged`. `{mode} {id}` commands are not
  continued.
- `agent_timeout` (default 7200 seconds, `0` no limit) applies per session. On
  expiry: `SIGTERM` the agent and its descendants, `SIGKILL` after
  `AGENT_KILL_GRACE_SECONDS`, print `agent timed out after N seconds`, exit 1.
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

`chitty run` prepares the worktree so the reviewer sees what would land:

1. An unfinished merge or rebase is an error for the human; no status change.
2. Uncommitted files (untracked and not ignored included): block for `human`
   with `Review blocked (work): ...`. No reviewer starts.
3. Merge local `main` into the branch, with `rerere.enabled=false`. Conflict:
   `git merge --abort`, move to `doing` with `Review failed (integration): ...`
   naming the files.
4. A branch that changes the Chitty config (`chitty.toml` or `[tool.chitty]`)
   or the managed block in `AGENTS.md`: move to `doing` with
   `Review failed (work): ...`.
5. Run `setup`, then `check`. Files left uncommitted: block for `human`. Check
   failure: move to `doing` with the last 20 lines, fenced, in
   `Review failed (work)`; no agent, no usage line, exit 0.

- These moves use the run's own actor, so they count towards
  `REVIEW_FAILURE_LIMIT`. Ctrl-C during the merge aborts it, exit 130.
- Work mode runs `setup` and `check` before claiming. A failure on a `doing`
  ticket adds a `Check failed before this session` note and the agent starts.
  On a `todo` ticket it fails with `check failed before <ID> started`, changing
  nothing.
- Entering `review`, or `review → done`, needs a clean worktree; `blocked` does
  not. `chitty check` reports dirty files on a branch in review.
- Reviewers record a verdict only; they never merge or remove branches or
  worktrees. A manual reviewer checks `git status --short` first and blocks a
  dirty ticket for `human`.

## Landing

On a pass, under the landing lock:

- The main checkout must be on `main_branch` and clean.
- Refused: uncommitted files in the worktree, a changed Chitty config, or a
  changed managed block in `AGENTS.md`, before or after merging.
- Merge `main_branch` into the branch, run `setup` and `check`, fast-forward
  `main_branch`, then remove the worktree and branch.
- A failure leaves the ticket as it was and asks a human to resolve it.
- Without `chitty run`: merge `main` into the branch in its worktree, run the
  checks, then only fast-forward `main`.

## Usage log

- One JSON line per run in `$XDG_DATA_HOME/chitty/usage/<project>.jsonl` (or
  the platform data directory): ticket, mode, actor, start, elapsed seconds,
  statuses.
- No token or cost data. Spend by model comes from the agent's session files,
  for Pi via `scripts/pi_tokens.py`.
