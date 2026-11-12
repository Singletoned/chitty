# Next action and runner

`chitty next` selects one active task across every context: the optional
`job_order` setting (default `review`, `doing`, `todo`), then high/medium
(including unset)/low priority and `TaskId`. It must be a non-empty list of
unique active statuses; omitted statuses are never selected.
Human-context tasks and tasks owned by `human` are excluded. A `todo` task with
an unmet dependency is excluded, while `doing` and `review` work remains
visible. `list` marks these exclusions with `👤`, `🔒`, or `⚠️` for a broken
dependency; `doing` and `review` ignore
dependencies. It prints `work ID` or `review ID`; `--json` and the read-only MCP
`next` tool return the same `{mode, id}` value. `--mode review` limits the
choice to `review` tasks and `--mode work` to `doing` and `todo`, in the same
order, filtering before dependencies are checked so a bad reference on a task
in the other mode does not stop this one. Repeating `--mode` allows each mode
given, so `--mode work --mode review` allows both; with no `--mode`, every mode
is allowed. With nothing left it prints `no next ticket` (or `no next ticket for
--mode MODE`, with several modes joined by ` or `, such as `review or work`) to
stderr and exits 3, a status of
its own, so an idle reviewer is distinguishable from a broken one, which exits
1. An idle queue includes one where every `todo` task waits on a dependency.
`chitty run` exits 3 in the same case. The MCP tool keeps the default.

A plain `chitty run` first retries landing non-archived `done` tickets that
still have a local branch named for their ID, in ID order. It stops after the
first landing and exits successfully; the next invocation refreshes setup before
selecting an agent ticket. `--ticket` skips this recovery pass.

`chitty run` requires `autocommit = true`, a configured `setup` command, and
an `agent_command`, unless `--agent NAME` selects an entry from `[agent_commands]`.
Use `chitty run --ticket ID` to choose a ticket instead of using the next selected ticket. A plain run skips owned `todo` and `doing` tickets, while still selecting owned `review` tickets; use `--owner NAME` to select that agent's tickets at any active status. `--owner human` and an empty owner are refused, as is combining `--owner` with `--ticket`.
`chitty run --mode MODE` selects as `chitty next --mode MODE` does, including
repeated `--mode` options, and is refused with `--ticket` before anything else
runs, because the ticket already decides its mode.
The command may include `{prompt}` as a single argument;
Chitty fills it with the role-specific `chitty guide <mode> <ID>` output after
splitting the command. It finds the main checkout even when invoked from another
worktree, creates or reuses the selected
ticket's worktree, runs parsed setup there, and claims a `todo` work ticket on
that branch before launching the parsed agent command. The agent uses the
`chitty` executable installed beside the runner's Python interpreter, rather
than a branch-local `chitty`; `pi` and `claude` come from the global `PATH`.
This does not change `chitty.toml` on the branch. The command must include
`{mode}` and `{id}`, unless it includes `{prompt}`; Chitty replaces them after
splitting, and arguments after
`--` pass through to the agent. Optional `work_model` and `review_model` add
`--model MODEL` for the selected mode, whether using the default or a named
agent command, only when neither that command nor forwarded arguments specify
`--model VALUE` or `--model=VALUE`. Existing model arguments take precedence,
and without a configured default the invocation is unchanged. Commands receiving
a default must accept the agent CLI option `--model`; Chitty has no `--model`
option of its own. It reopens the ticket worktree after the agent
exits and succeeds only if the task's committed status changed. An exit 0 with
the status unchanged continues the same session, if the command has `{prompt}`:
the command runs again with the continuation prompt in place of `{prompt}` and
`-c` appended after the other arguments, at most `MAX_CONTINUATIONS` (5) times
per run, then fails with `was unchanged`. A `{mode} {id}` command is not
continued. Each session has its own `agent_timeout`, and one usage line covers
the run. This makes
`chitty run --loop --mode work -- --model MODEL` keeps running, waiting 60
seconds after each successful run or idle queue before trying again. Each
attempt starts a fresh `chitty run` process so a completed landing cannot leave
the next ticket running with code loaded before that landing. It accepts
`--mode`, `--owner`, `--agent`, and forwarded agent arguments; `--ticket` cannot
be used with `--loop`. Without `--loop`, an idle queue still exits 3. Each loop
pass checks configuration and refreshes setup before selecting, so a broken
configuration stops the loop with exit 1. An agent's or setup's own failure
also stops it with exit 1. Interrupting the agent, setup, or idle wait stops
with exit 130 without a traceback.

Before a review (decided with the human, 2026-11-03), after the run's actor is
set, `chitty run` prepares the ticket's worktree so the reviewer sees exactly
what would land:

1. An unfinished merge or rebase, for example after a crash, is a loud error for
   the human, with no status change.
2. Uncommitted changes, including untracked but not ignored files, block the
   ticket for `human` immediately with `Review blocked (work): ...` listing
   them. No reviewer starts and the human decides when to resume.
3. It merges the local `main` into the branch. On a conflict it runs
   `git merge --abort` and moves the ticket to `doing` with `Review failed
   (integration): ...` naming the conflicting files, for the worker to resolve
   in a fresh session. The merge runs with `rerere.enabled=false`, so a
   resolution Git recorded for another branch is never replayed unchecked.
4. Only then does `setup` run, because the merge can change dependencies.
5. `check` runs in the ticket worktree after setup, with combined output
   captured. If setup or check leaves uncommitted files in review mode, block
   for `human` before launching the reviewer. Otherwise a check failure moves
   the ticket to `doing` with the last
   20 output lines, fenced as a code block so they cannot break the ticket's
   Markdown, in a `Review failed (work)` note and starts no agent. In work mode,
   a `doing` ticket gets a note-only `Check failed before this session: ...`
   edit and the agent starts normally; a `todo` ticket raises an error with
   `check failed before <ID> started: ...`, changing nothing and starting no
   agent. In all work-mode cases setup and check still run before the agent
   claim.

Entering `review` or passing it to `done` through the shared store requires
a clean current worktree; a dirty branch may still be moved to `blocked` for
human resolution. `chitty check` reports dirty files on the current ticket
branch while in
review, but allows dirty `doing` work during development. Direct manual
reviewers also check `git status --short` first and block dirty tickets for
`human` rather than returning them to a worker. A review check failure starts
no agent, writes no usage line, and `chitty run`
exits 0 because the status changed, printing the change. The move goes through
`Repo.edit` under the run's own actor, which never worked on the ticket, so it
counts with reviewers' failures towards `REVIEW_FAILURE_LIMIT`. A work-mode
failure on a `todo` ticket exits 1 without changing the ticket; a failure on a
`doing` ticket proceeds to the agent, which can fix it.
Interrupting the merge aborts it and exits 130. A clean merge is not
repeated or re-reviewed if `main` moves during the review; landing is
`TASK-131`. Reviewers record the verdict and do not merge or remove branches
or worktrees. On a pass, `chitty run` lands by fast-forwarding `main` after the
branch has been integrated with `main` and configured checks pass. Without
`chitty run`, merge `main` into the ticket branch in its worktree, run the
configured checks, and only then fast-forward `main`.

The optional root-level `agent_timeout` is a non-negative TOML integer in seconds. It defaults to 7200; `0` disables the limit. On expiry, `chitty run` terminates the agent and its descendants, then escalates from `SIGTERM` to `SIGKILL` after a short grace period, reports `agent timed out after N seconds`, and exits 1. The agent remains in the runner's process group and session so terminal input and Ctrl-C behave normally. Timeout is an agent failure: the run is logged and `--loop` stops.

Each agent session appends one JSON line to the machine-local usage log at
`$XDG_DATA_HOME/chitty/usage/<project>.jsonl` (or the platform data directory
when `XDG_DATA_HOME` is unset). The line records the ticket, mode, actor,
start time, elapsed seconds, and statuses. `chitty run` does not read token or
cost data from the agent. Spend by model comes from the agent's session files:
run `scripts/pi_tokens.py` on the Pi session directories.
