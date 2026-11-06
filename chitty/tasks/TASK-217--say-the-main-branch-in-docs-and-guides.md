---
title: Say "the main branch" in docs and guides
status: review
priority: medium
depends_on:
  - TASK-216
created: 2026-11-06
---

## Description

After `TASK-216`, the integration branch is the optional `main_branch` setting (default `main`, `TASK-214`). Wherever the guides and docs mean the integration branch, say "the main branch" instead of "`main`". Leave text about the primary checkout ("main checkout") alone; it is never backticked.

- `src/chitty/guide.md` lines 13 and 31, and `src/chitty/roles/review.md` line 16. Use plain "the main branch". Don't add "(`main_branch` in `chitty.toml`)": the block is copied into every repository's `AGENTS.md`, `TASK-143` is shrinking it, and some repositories configure Chitty in `pyproject.toml` instead. `TASK-151` also rewrites the merge sentences at guide line 31 and review line 16; whichever ticket lands second adapts to the other.
- `README.md` line 125, and `PLAN.md` lines 62, 134, 529, 716, 722 and 735.
- Leave `README.md` line 34 and `PLAN.md` lines 650–651. They describe developing Chitty itself, whose branch is `main`.
- `PLAN.md`'s `## Config` section: add a commented `# main_branch = "master"` line to its TOML block, and a sentence saying the setting is optional, defaults to `main`, and that `chitty init` writes it only for a new repository on another branch.

Bump `__version__` at patch level. `scripts/check_version_bump.py` requires a bump for any change to `src/chitty/guide.md` or `src/chitty/roles/`. Don't run `chitty init` on the branch (`TASK-212`). This repository's own `AGENTS.md` keeps "`main`" until the main checkout's upgrade regenerates it after landing; reviewers should expect that.

Out of scope: `scripts/check_version_bump.py`'s own hard-coded `main`, which only runs in this repository.

## Acceptance Criteria

- [x] Run ``grep -n '`main`' src/chitty/guide.md src/chitty/roles/*.md README.md PLAN.md``: it matches only `README.md` line 34 and `PLAN.md` lines 650–651. `PLAN.md`'s `## Config` section documents `main_branch` as optional with default `main`.
- [x] `__version__` is bumped and `make check` passes.

## Plan

Update the specified guide, role, README, and PLAN references to say "the main branch" while preserving the two repository-development references. Document the optional main_branch setting in PLAN.md, bump the package patch version, then run the required grep and make check.

## Notes

Cold read 1 (Opus, read-only; docs only, so nothing to run). Outcomes:
- The criterion couldn't pass, because documenting the default would itself match: fixed, the default is written as code and the allowed matches are listed.
- The broken code span around the grep: fixed, it uses double backticks.
- Version-bump reasoning: fixed, the bump is required by `check_version_bump.py`; only `guide.md` is the managed block.
- `(`main_branch` in `chitty.toml`)` in the managed guide: rejected, plain "the main branch", because of `TASK-143` and `pyproject` configs.
- `README:34` and `PLAN:650–651`: decided, leave them, because they're about this repository.
- Overlap with `TASK-151`'s merge sentences: noted.
- This repository's stale `AGENTS.md`: noted for reviewers.
- `check_version_bump.py` hard-codes `main`: rejected as out of scope, because it only runs here.
- "from the main branch … never implement in the main checkout" reads confusingly: accepted as accurate.

Verified the grep leaves only README.md line 34 and PLAN.md lines 660-661 (the repository-development references), and PLAN.md documents optional main_branch with default main. make install && make format && make check passed: 359 Python tests and Node tests passed.

## Summary

Updated guide, review role, README, and PLAN wording to say the main branch; documented optional main_branch configuration; bumped __version__ to 0.1.40. Verification: required grep, git diff --check, and make install && make format && make check all passed. No follow-ups.

## History

- 2026-11-06T16:48:08Z youthful-toad → backlog
- 2026-11-06T16:48:23Z youthful-toad: changed dependencies
- 2026-11-06T16:48:41Z youthful-toad: changed description
- 2026-11-06T16:49:20Z youthful-toad: changed description
- 2026-11-06T17:01:21Z youthful-toad: changed description, acceptance criteria, notes
- 2026-11-06T17:01:21Z youthful-toad backlog → todo
- 2026-11-06T21:25:37Z kind-gannet todo → doing
- 2026-11-06T21:25:59Z kind-gannet: wrote the plan
- 2026-11-06T21:28:31Z kind-gannet: changed notes, summary; ticked acceptance criteria
- 2026-11-06T21:28:31Z kind-gannet doing → review
