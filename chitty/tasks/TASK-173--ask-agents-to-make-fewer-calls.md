---
title: Ask agents to make fewer calls
status: doing
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

- [x] A test shows `chitty guide work` and `chitty guide review` containing `repeated --check`, `in one call`, `joined with` and `autocommit = true`, and `__version__` is bumped above `main`'s

## Plan

Update the shipped work and review role guidance with the four batching/autocommit recommendations, add or extend a guide-output regression test, bump __version__, run the full check suite, and record verified criteria.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: this conflicted with "tick only after verifying", so it now says to verify first; `make format` does not exist in every repository; and the test now names what it checks. `TASK-174`'s successor or the planning session re-runs the scripts afterwards. Repeated `--check` was tried on `TASK-80`, and it works.

Review failed (integration): rebasing onto `main` conflicts in `tests/test_cli.py`.

Verified the guide-output regression test for both roles and confirmed version 0.1.35 is above main's 0.1.34. Full make format && make check passes (278 Python tests and Node tests).

Owner set to `human` so the review loop skips this until `TASK-212` lands: the branch records `0.1.35` and `main`'s `0.1.34` `chitty` refuses to write here. Clear the owner then.

Owner cleared: the branch now has `main`'s `chitty.toml` again, so `main`'s `chitty` can write here.

Review failed (integration): rebasing onto `main` conflicts in `chitty.toml`.

## Summary

Updated work/review guides with batched-call and autocommit guidance, added guide-output regression coverage, and bumped Chitty to 0.1.35. Verified with full make format && make check; follow-up remains to rerun TASK-170 measurement scripts.

## History

- 2026-11-04T21:41:08Z mellow-newt → backlog
- 2026-11-04T21:41:38Z mellow-newt: changed description
- 2026-11-04T21:44:28Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T21:44:29Z mellow-newt backlog → todo
- 2026-11-05T23:09:47Z lively-newt todo → doing
- 2026-11-05T23:10:00Z lively-newt: wrote the plan
- 2026-11-05T23:19:56Z lively-newt: changed summary; ticked acceptance criteria
- 2026-11-05T23:20:09Z lively-newt doing → review
- 2026-11-06T14:39:20Z friendly-heron: changed notes
- 2026-11-06T14:39:20Z friendly-heron review → doing
- 2026-11-06T15:58:09Z lively-falcon: changed notes, summary; ticked acceptance criteria
- 2026-11-06T15:58:09Z lively-falcon doing → review
- 2026-11-06T16:25:03Z youthful-toad: changed owner, notes
- 2026-11-06T16:43:38Z youthful-toad: changed owner, notes
- 2026-11-06T16:47:49Z quick-puffin: changed notes
- 2026-11-06T16:47:49Z quick-puffin review → doing
