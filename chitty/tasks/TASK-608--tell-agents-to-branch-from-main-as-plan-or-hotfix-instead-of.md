---
title: Tell agents to branch from `main` as `plan/` or `hotfix/` instead of committing on it
status: doing
labels:
  - untestable
owner: friendly-zinc-dormouse
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

## History

- 2026-11-23T10:23:59Z witty-russet-gannet → backlog
- 2026-11-23T10:24:00Z witty-russet-gannet: changed notes
- 2026-11-23T10:54:18Z witty-russet-gannet: changed title, labels, owner, description
- 2026-11-23T10:54:18Z witty-russet-gannet backlog → todo
- 2026-11-23T12:01:28Z friendly-zinc-dormouse: changed owner
- 2026-11-23T12:01:28Z friendly-zinc-dormouse todo → doing
