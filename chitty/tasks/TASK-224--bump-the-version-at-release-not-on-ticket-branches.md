---
title: Bump the version at release, not on ticket branches
status: done
priority: high
created: 2026-11-06
---

## Description

Every ticket that changes the guides or setup bumps `__version__` on its branch, on the same line of `src/chitty/__init__.py`. So whenever one lands, every other open one conflicts at its review merge. On 2026-11-06 four tickets in review all carried `0.1.41`. The version only matters once it is published, so the human decided to bump it at release time.

1. **Branches stop bumping.** Remove `uv run python scripts/check_version_bump.py` from the `check` target in `Makefile`, delete `scripts/check_version_bump.py` and `tests/test_version_bump.py`, and rewrite this repository's `AGENTS.md` rule (the bullet beginning "Any change that existing repos only pick up by re-running `chitty init`") to say branches never change `__version__`. Edit only the hand-written part of `AGENTS.md`, above the managed block; this is this repository's release process, not Chitty's guide.
2. **A `needs-minor` label.** Whoever writes, works or reviews a ticket may add it (`chitty edit ID -l needs-minor`) when the change is one users must notice or act on: a new required setting, a changed default or selection rule, something that needs `chitty init` re-run, or a removed command or option. Labels merge without conflict. Say this in this repository's `AGENTS.md`, next to the release bullet.
3. **`make release` chooses the bump.** Add `scripts/release_version.py`, which:
   - finds the last `v*` tag;
   - lists ticket files under `chitty/` that changed since it (`git diff --name-only <tag>..HEAD -- chitty/`), including archived ones, and reads their labels;
   - prints the next version, counting from the higher of the last tag's version and the current `__version__`: minor (`0.1.40` → `0.2.0`) if any has `needs-minor`, otherwise patch. Counting from the tag alone would go backwards: on 2026-11-06 the last tag was `v0.1.35` while `main` said `0.1.40`, and other repositories running the editable `chitty` from `main` may already record `0.1.40`;
   - prints the labelled tickets to stderr, as a start for release notes.
   The `release` target keeps its existing guards (on `main`, clean tree, not behind `origin/main`). It then writes the new version into `src/chitty/__init__.py`, commits `Release <version>`, tags and pushes as today. With no tag yet, the script fails, naming the problem.

Decisions:
- Read labels with Chitty's own parser (`chitty.model.parse`), so a malformed ticket fails the release loudly.
- Count from the highest `v*` tag by version, not the most recent tag.
- Labels on tickets deleted since the tag are lost. That's accepted, because this repository archives by moving (`archive = "move"`); say so in a comment.
- If the push fails, `make release` prints how to undo the local `Release` commit and tag (`git tag -d v<version> && git reset --hard HEAD~1`).

Out of scope: major versions, changelogs, and Chitty's own `chitty.toml` (the main checkout's setup refresh updates `chitty_version` after release).

## Acceptance Criteria

- [x] `make check` no longer runs the version-bump check (the script and its test are gone), `mate --list` still describes `release`, and `AGENTS.md` says branches don't bump `__version__` and explains `needs-minor`.
- [x] Tests of `scripts/release_version.py` in a temporary repository show: a patch bump with no labelled ticket since the last tag; a minor bump when an archived or active ticket changed since the tag has `needs-minor`; a ticket labelled only before the tag being ignored; counting from `__version__` when it is ahead of the tag; and a missing tag failing with a clear error.

## Plan

Inspect the release workflow and Chitty parser APIs, then replace branch version checks with a release-time script and Makefile recipe. Add focused temporary-repository tests for tag selection, patch/minor decisions, archived and active ticket labels, current-version precedence, and missing tags. Update the hand-written release guidance in AGENTS.md, remove obsolete checker code/tests, run the focused regression tests before and after implementation, then run format and full checks.

## Notes

Cold read 1 (Sonnet, `refs/cold-read/TASK-224/1`; 8 tests failed first and then passed; `make check` OK; the release recipe itself was never run, by instruction). Outcomes:
- How labels are read: decided, Chitty's parser.
- Labels on tickets deleted since the tag are lost: accepted for this repository, with a comment.
- A failed push leaves a local commit and tag: fixed, `make release` prints the undo.
- Highest tag rather than latest: decided.
- `release.yml` still checks the tag against `__version__`: confirmed, because the bump is committed before tagging.
- `PLAN.md`'s "Stack" note about bumps on `main`: still accurate, unchanged.

Verified with the five temporary-repository release tests, mate --list, make -n release, direct release-version execution, and make format && make check (361 Python tests and Node tests passed). chitty fix reported existing Markdown delimiter warnings in unrelated tickets; it made no repairs.

Reviewed: release-time version selection, label handling, Makefile guards, focused tests, mate --list, and make format && make check all pass.
1: pass - Branch checks and release guidance are updated; mate --list includes release.
2: pass - Temporary repository release tests cover patch, minor, archived/active labels, pre-tag labels, version precedence, and missing tags; full checks pass.

## Summary

Implemented release-time version selection in scripts/release_version.py, including highest valid v* tag selection, current-version precedence, patch/minor ticket-label detection, archived tickets, and clear missing-tag failure. Removed branch version enforcement, updated release guidance, and changed make release to commit, tag, push, and report push rollback instructions. Handoff: review the compact Makefile version-write command and release behavior. Verification: focused release tests and full make format && make check pass. Follow-ups: none.

## History

- 2026-11-06T22:01:24Z youthful-toad → backlog
- 2026-11-06T22:01:44Z youthful-toad: changed description, acceptance criteria
- 2026-11-06T22:04:43Z youthful-toad: changed description, notes
- 2026-11-06T22:04:43Z youthful-toad backlog → todo
- 2026-11-08T09:27:35Z upbeat-gannet todo → doing
- 2026-11-08T09:27:54Z upbeat-gannet: wrote the plan
- 2026-11-08T09:32:44Z upbeat-gannet: changed notes, summary; ticked acceptance criteria
- 2026-11-08T09:32:44Z upbeat-gannet doing → review
- 2026-11-08T10:25:39Z eager-zander: changed notes; ticked acceptance criteria
- 2026-11-08T10:25:39Z eager-zander review → done
