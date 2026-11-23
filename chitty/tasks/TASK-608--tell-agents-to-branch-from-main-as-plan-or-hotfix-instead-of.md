---
title: Tell agents to branch from `main` as `plan/` or `hotfix/` instead of committing on it
status: review
labels:
  - untestable
owner: plucky-indigo-eel
created: 2026-11-23
---

## Description

Agents still commit fixes directly on `main` when no ticket covers them, for example a repair to `make release` (the suggestion that prompted this, 2026-11-23). With several sessions committing in the same checkout, that is how changes collide and skip review. This repository's own `AGENTS.md` already forbids it; the advice should reach every repository that uses Chitty.

Decision (the person, 2026-11-23): stop changing `main` whenever a branch is easy, and name every branch that starts from `main` and is meant to merge back by its kind, using a slash, matching the `plan/` prefix Chitty already recognises (`src/chitty/store.py:894`, TASK-521):

- `task-<n>`: ticket work, as the runner creates today (unchanged).
- `plan/<name>`: planning sessions.
- `hotfix/<name>`: a fix outside any ticket, such as repairing a broken release script.

Change:

- `src/chitty/guide.md` (the managed block every repository's `AGENTS.md` gets): add a short paragraph saying the above, and that such work happens in its own worktree, passes the configured checks, and then fast-forwards `main`. Keep it general: no Python, no names from this repository. Do not tell agents to move Chitty's own ticket writes off `main`; that is TASK-340's job.
- `docs/plan/pipeline-and-feedback.md` (or the plan file that covers branches, if a better one exists): record the decision and the three prefixes.
- Update any test that pins the managed block's text.

Out of scope: code that treats `hotfix/` branches specially; a `chitty land` command (TASK-340, which should recognise these prefixes).

## Notes

Suggestion origin: chitty

Review failed (work): the new managed-block sentence in `src/chitty/guide.md` lists `task-<n>` among the branches whose author should "run the checks, then fast-forward `main`". In the runner block printed straight after it (`tests/fixtures/guide-runner-expected.md`), "a worker never lands its own ticket" and the runner or a passing reviewer lands it. A worker reading both gets two contradictory landing rules for ticket branches. The ticket says `task-<n>` is "unchanged". Fix: make the fast-forward apply only to `plan/` and `hotfix/` branches. For example: "Never commit your changes on `main`. Outside ticket work, branch from it in a worktree as `plan/<name>` or `hotfix/<name>`, run the checks, then fast-forward `main`." This keeps within the 75-word budget. Update the fixture, the `TICKETS_TEXT_END` marker and the `docs/plan/pipeline-and-feedback.md` entry to match.
The ticket has no acceptance criteria (`untestable`). `make check` passed in the worktree (1170 tests).

## Summary

Added one paragraph to `src/chitty/guide.md`, the managed block: "Never commit your changes on `main`. Outside ticket work, branch from it in a worktree as `plan/<name>` or `hotfix/<name>`, run the checks, then fast-forward `main`." It says "your changes", so Chitty's own ticket writes on `main` are left to `TASK-340`.

Review fix: the earlier wording listed `task-<n>` among branches the author fast-forwards, contradicting "a worker never lands its own ticket" in the runner block. The fast-forward now applies only outside ticket work; `task-<n>` branches are unchanged and still land after review.

Recorded the decision and the three prefixes under Concurrency in `docs/plan/pipeline-and-feedback.md`, stating that ticket branches still land only after review. Updated the pinned snapshot `tests/fixtures/guide-runner-expected.md` and the `TICKETS_TEXT_END` marker in `tests/test_guide_workflow_block.py`. Rebased onto `main` after `TASK-640` removed the word-budget test.

Verification: `make check` passed (1156 tests). Follow-up: this repository's own `AGENTS.md` block updates when the main checkout's `chitty init` upgrades it after landing.

## History

- 2026-11-23T10:23:59Z witty-russet-gannet → backlog
- 2026-11-23T10:24:00Z witty-russet-gannet: changed notes
- 2026-11-23T10:54:18Z witty-russet-gannet: changed title, labels, owner, description
- 2026-11-23T10:54:18Z witty-russet-gannet backlog → todo
- 2026-11-23T12:01:28Z friendly-zinc-dormouse: changed owner
- 2026-11-23T12:01:28Z friendly-zinc-dormouse todo → doing
- 2026-11-23T12:18:35Z friendly-zinc-dormouse: changed summary
- 2026-11-23T12:18:35Z friendly-zinc-dormouse doing → review
- 2026-11-23T13:32:42Z able-amber-falcon: changed notes
- 2026-11-23T13:32:42Z able-amber-falcon review → doing
- 2026-11-23T14:27:22Z plucky-indigo-eel: changed owner
- 2026-11-23T14:34:49Z plucky-indigo-eel: changed summary
- 2026-11-23T14:34:49Z plucky-indigo-eel doing → review
