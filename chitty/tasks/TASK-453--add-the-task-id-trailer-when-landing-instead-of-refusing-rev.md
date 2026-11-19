---
title: "Add the `Task: <ID>` trailer when landing, instead of refusing review without it"
status: planning
priority: high
created: 2026-11-19
---

## Description

Since `TASK-346`, `Repo.edit` (`src/chitty/store.py`) refuses `-s review` when a non-`chitty:` commit on the branch lacks a `Task: <ID>` line in its last paragraph (`git.commits_missing_trailer` over `git.branch_commits`). Agents keep tripping on it: the only instruction is one line in `src/chitty/roles/work.md`, so any session that did not load that guide misses it (a human-directed session, a repair, an agent fixing a blocked ticket; seen on `TASK-403` on 2026-11-19), and the error suggests `git rebase -i`, which agent harnesses cannot run. The trailer only matters after landing, for `git log --grep <ID>` and the repair guide's search for lost work; before that, `main..task-<n>` already identifies the commits.

Decided with the owner 2026-11-19: Chitty adds the trailer itself when it lands, and the review refusal goes.

Decisions:

- Pure function `with_task_trailer(message: str, task_id: TaskId) -> str` in `src/chitty/git.py`. It returns `message` unchanged when `commits_missing_trailer([Commit("", message)], task_id)` is empty (a `chitty: ` commit, or the trailer already present). Otherwise, with `body = message.rstrip()`: if the last paragraph of `body` (lines after the last blank line; a one-paragraph message has no trailer block) consists only of lines matching `^[A-Za-z0-9-]+: .+$`, return `body + "\nTask: <ID>\n"`; else return `body + "\n\nTask: <ID>\n"`.
- New `git.add_task_trailers(root: Path, main_branch: str, branch: str, task_id: TaskId) -> int` returns how many commits it rewrote. It reads `branch_commits(root, main_branch)`; if none needs a trailer it changes nothing and returns 0. Otherwise it replays every commit of `main_branch..HEAD` oldest first with `git commit-tree <tree> -p <new parent> -F -` (the message from `with_task_trailer`), keeping each commit's author name, email and date (`GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_AUTHOR_DATE` from `git show -s --format=...`), then moves the branch with `git update-ref refs/heads/<branch> <new tip> <old tip>`. Trees do not change, so the worktree files and index stay as they are. It raises `ChittyError` if `main_branch..HEAD` holds a merge commit (cannot happen after the landing rebase).
- `_land_locked` (`src/chitty/run.py`) calls it in each landing attempt, right after a successful `git.rebase_onto` and before the config and protected-path checks, so setup and the landing check run on the rewritten commits.
- Delete the trailer refusal in `Repo.edit` (the `if entering_review:` block that calls `commits_missing_trailer`). Keep `commits_missing_trailer`.
- Guides: in `src/chitty/roles/work.md`, replace `ending with a \`Task: <ID>\` trailer; \`chitty edit -s review\` refuses branch commits without one.` with text saying Chitty adds a `Task: <ID>` trailer to each commit when it lands the ticket, so a worker need not write one. Update `docs/plan/` where it describes the review refusal (`git grep -n "Task:" docs/plan`).
- Out of scope: landings done by hand without `chitty run`.

Tests use Hypothesis (the repository tool) for the pure function, in a new `tests/test_property_task_trailer.py`; the landing test uses real Git, following `tests/test_landing.py`.

## Acceptance Criteria

- [ ] Property: for messages drawn from lines of `st.text()` without newlines, mixed with trailer-like lines (`Key: value`), blank lines, a `chitty: ` subject, and a `Task: <ID>` line for the same or another ID, at drawn positions: `commits_missing_trailer` of the result is empty; applying `with_task_trailer` twice equals once; the result starts with `message.rstrip()`, or equals `message` when nothing was missing; exactly one line `Task: <ID>` was added when something was missing. It fails today (`with_task_trailer` does not exist; first stub it raising `NotImplementedError`).
- [ ] A landing test with real Git: a ticket branch with three commits (one with no trailer, one whose last paragraph is `Signed-off-by: A <a@example.com>`, one already ending `Task: TASK-1`) lands through `chitty run`; afterwards each of those commits on `main` has exactly one `Task: TASK-1` line in its last paragraph, keeps its author and author date, and the trees match the branch before landing. It fails today.
- [ ] `chitty edit TASK-1 -s review` on a branch whose commits have no trailer succeeds; the existing test that expects the refusal (find it with `git grep -n "lack a Task" tests`) is removed or inverted. `make check` passes.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:28Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:29Z sunny-white-dormouse: changed notes
- 2026-11-19T21:20:12Z sunny-white-dormouse: changed title, priority, description, acceptance criteria
- 2026-11-19T21:20:12Z sunny-white-dormouse backlog → planning
