---
title: Ask agents to make fewer calls
status: backlog
priority: medium
depends_on:
  - TASK-142
parent: TASK-106
created: 2026-11-04
---

## Description

From `docs/pi-token-usage.md`, recommendations 3 and 5. Each call re-sends the whole context, averaging $0.018 however small the command is, and `chitty` and `git` are 29% of spend. Agents average 1.11 tools per call, and 538 single-read calls directly followed another. How well the model follows such instructions has not been checked, so measure it afterwards by re-running the scripts from `TASK-170`.

Add to `src/chitty/roles/work.md` and `review.md`, keeping them about 30 lines: tick criteria and add a note in one `chitty edit`, at each stage, not one per step; request several reads in one call when none depends on another; run `make format && make check` as one step, in the repository's own form. `chitty` commits its own writes when `autocommit` is on, so a separate `git status` or `git add` after one is not needed.

Out of scope: having `chitty` do more of the Git steps, which needs its own design once this is measured.

## Acceptance Criteria

- [ ] `chitty guide work` and `chitty guide review` contain these instructions, shown by a test, and `__version__` is bumped above `main`'s

## History

- 2026-11-04T21:41:08Z mellow-newt → backlog
- 2026-11-04T21:41:38Z mellow-newt: changed description
