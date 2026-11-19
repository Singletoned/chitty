---
title: "Add the `Task: <ID>` trailer when landing, instead of refusing review without it"
status: doing
priority: high
created: 2026-11-19
---

## Description

Since `TASK-346`, `Repo.edit` (`src/chitty/store.py`) refuses `-s review` when a non-`chitty:` commit on the branch lacks a `Task: <ID>` line in its last paragraph (`git.commits_missing_trailer` over `git.branch_commits`). Agents keep tripping on it: the only instruction is one line in `src/chitty/roles/work.md`, so any session that did not load that guide misses it (a human-directed session, a repair, an agent fixing a blocked ticket; seen on `TASK-403` on 2026-11-19), and the error suggests `git rebase -i`, which agent harnesses cannot run. The trailer only matters after landing, for `git log --grep <ID>` and the repair guide's search for lost work; before that, `main..task-<n>` already identifies the commits.

Decided with the owner 2026-11-19: Chitty adds the trailer itself when it lands, and the review refusal goes.

Decisions:

- Pure function `with_task_trailer(message: str, task_id: TaskId) -> str` in `src/chitty/git.py`. It returns `message` unchanged when `commits_missing_trailer([Commit("", message)], task_id)` is empty (a `chitty: ` commit, or the trailer already present). Lines and blank lines follow `commits_missing_trailer` exactly (`splitlines()`, blank means `not line.strip()`). A message that is empty or only whitespace becomes `Task: <ID>\n`. Otherwise, with `body = message.rstrip()`: if the last paragraph of `body` (lines after the last blank line; a one-paragraph message has no trailer block) consists only of lines matching `^[A-Za-z0-9-]+: .+$`, return `body + "\nTask: <ID>\n"`; else return `body + "\n\nTask: <ID>\n"`.
- New `git.add_task_trailers(root: Path, main_branch: str, branch: str, task_id: TaskId) -> int` returns how many commits it rewrote. Callers pass the ticket worktree as `root` (in `_land_locked`, `worktree`), where `HEAD` is the ticket branch. It first raises `ChittyError` if `git rev-list --merges <main_branch>..HEAD` is not empty (cannot happen after the landing rebase). It reads `branch_commits(root, main_branch)`; if none needs a trailer it changes nothing and returns 0. Otherwise it replays every commit of `main_branch..HEAD` oldest first with `git commit-tree <tree> -p <new parent> -F -` (the message from `with_task_trailer`), keeping each commit's author name, email and date (`GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` and `GIT_AUTHOR_DATE` from `git show -s --format=%an%x00%ae%x00%ad --date=raw`), with the committer and committer date left to Git (the current user and time), then moves the branch with `git update-ref refs/heads/<branch> <new tip> <old tip>`. Trees do not change, so the worktree files and index stay as they are. A failing Git command raises `ChittyError` carrying its stderr, as `_git` does.
- `_land_locked` (`src/chitty/run.py`) calls it in each landing attempt, right after a successful `git.rebase_onto` and before the config and protected-path checks, so setup and the landing check run on the rewritten commits.
- Delete the trailer refusal in `Repo.edit` (the `if entering_review:` block that calls `commits_missing_trailer`). Keep `commits_missing_trailer`.
- Guides: in `src/chitty/roles/work.md`, replace the text from `ending with a` to `refuses branch commits without one.` (it wraps across lines 23 and 24) with text saying Chitty adds a `Task: <ID>` trailer to each commit when it lands the ticket, so a worker need not write one; in `tests/test_guide_work_commits.py`, replace the phrases `"Task: <ID>"` and `"refuses branch commits without one"` with phrases from the new text. In `README.md`, the sentence starting `Commits for task work should end with` says instead that `chitty run` adds a `Task: <ID>` trailer to each commit of a ticket branch when it lands it, so `git log --grep <ID>` finds the code.
- Out of scope: landings done by hand without `chitty run`.

Tests use Hypothesis (the repository tool) for the pure function, in a new `tests/test_property_task_trailer.py`; the landing test uses real Git, following `tests/test_landing.py`.

## Acceptance Criteria

- [ ] Property: messages are built from lines over the alphabet `st.characters(min_codepoint=32, max_codepoint=126)` plus `\t`, mixed with trailer-like lines (`Key: value`, unindented), blank lines, a `chitty: ` subject and a `Task: <ID>` line for `TASK-1` or `TASK-10`, joined with `\n` at drawn positions; the ID passed is `TASK-1`. For all of them: `commits_missing_trailer` of the result is empty; applying `with_task_trailer` twice equals once; the result equals `message` when nothing was missing, else starts with `message.rstrip()` and has exactly one more `Task: TASK-1` line. Fixed examples: `""` gives `Task: TASK-1\n`; `Fix\n\nSigned-off-by: A <a@example.com>` gives that plus `\nTask: TASK-1\n`; `Fix` gives `Fix\n\nTask: TASK-1\n`. Wrong versions run against these tests, failing test recorded in a note: always appending `\n\nTask: <ID>`; never joining an existing trailer paragraph.
- [ ] A landing test with real Git: a ticket branch with three commits with distinct subjects (one with no trailer, one whose last paragraph is `Signed-off-by: A <a@example.com>`, one already ending `Task: TASK-1`) lands through `chitty run`; afterwards each commit on `main`, matched by subject, has `Task: TASK-1` exactly once among the `splitlines()` of its last paragraph, the same author and raw author date (`%ad` with `--date=raw`), and the same `^{tree}` as before landing. Direct `add_task_trailers` tests: on a branch whose commits all have the trailer it returns 0 and `HEAD` is unchanged; on a branch with a merge commit it raises `ChittyError`. It fails today.
- [ ] `chitty edit TASK-1 -s review` on a branch whose commits have no trailer exits 0 and the ticket is in `review`: invert `TestReviewTrailerGate.test_review_entry_requires_trailer` in `tests/test_review_trailers.py` to assert this, dropping its stderr assertions. `make check` passes.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:28Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:29Z sunny-white-dormouse: changed notes
- 2026-11-19T21:20:12Z sunny-white-dormouse: changed title, priority, description, acceptance criteria
- 2026-11-19T21:20:12Z sunny-white-dormouse backlog → planning
- 2026-11-19T21:20:41Z sunny-white-dormouse: changed description
- 2026-11-19T21:20:41Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:22:53Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:22:53Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:22:58Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:24:34Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:24:34Z sunny-white-dormouse cold-read → todo
- 2026-11-19T23:23:20Z quick-navy-raven todo → doing
