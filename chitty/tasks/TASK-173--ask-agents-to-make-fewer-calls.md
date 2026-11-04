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

Add to `src/chitty/roles/work.md` and `review.md`, keeping them about 30 lines, with wording close to this. These ship to every repository, so do not name `make`:

- "Verify first, then tick every verified criterion and add your note in one `chitty edit`, using repeated `--check`, rather than one call for each."
- "Request several reads in one call when none depends on another."
- "Run the repository's format and check commands in one shell call, joined with `&&`."
- "With `autocommit = true`, Chitty commits its own writes, so `git status` or `git add` after one is not needed."

Out of scope: having `chitty` do more of the Git steps, which needs its own design once this is measured.

## Acceptance Criteria

- [ ] A test shows `chitty guide work` and `chitty guide review` containing `repeated --check`, `in one call`, `joined with` and `autocommit = true`, and `__version__` is bumped above `main`'s

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: this conflicted with "tick only after verifying", so it now says to verify first; `make format` does not exist in every repository; and the test now names what it checks. `TASK-174`'s successor or the planning session re-runs the scripts afterwards. Repeated `--check` was tried on `TASK-80`, and it works.

## History

- 2026-11-04T21:41:08Z mellow-newt → backlog
- 2026-11-04T21:41:38Z mellow-newt: changed description
- 2026-11-04T21:44:28Z mellow-newt: changed description, acceptance criteria, notes
