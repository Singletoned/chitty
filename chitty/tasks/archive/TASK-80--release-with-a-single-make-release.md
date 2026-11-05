---
title: Release with a single `make release`
status: done
priority: high
created: 2026-11-01
---

## Description

Add `make release`: tag the version already in `src/chitty/__init__.py` and push it, so `release.yml` publishes it. It refuses unless on `main`, with a clean tree, with `origin/main` contained in `HEAD`, and with `make check` passing. Pushing the branch and tag is atomic, and an existing tag fails. After the push it writes the version to `$XDG_DATA_HOME/chitty/pending-release`, which says a release is on its way, for the upgrade alert.

Rewritten 2026-11-04 at the human's prompting: this waited since 2026-11-01 while the ticket grew a scheme for choosing minor or patch. `__version__` is already bumped in each change that needs it, so releasing only has to tag it, and the per-change rule stays.

## Acceptance Criteria

- [x] A trial with a local bare `origin` shows `make release` refusing off `main`, with a dirty tree and when behind `origin/main`, and otherwise pushing `main` and the tag and writing `pending-release`
- [x] `AGENTS.md` describes releasing with `make release`, and `mate --list` shows the target

## Plan

Add a `release` target that tags the existing version, and try it against a local bare `origin`.

## Notes

Blocked pending HUMAN-6: the specified `init` comparison always changes `chitty_version`, so it cannot distinguish patch from minor. Implementation would encode an unintended always-minor policy.

Unblocked: HUMAN-6 decided that the comparison ignores `chitty_version` (criterion rewritten, now number 4).

Blocked on TASK-83: `chitty init` reads the installed package metadata version, so release automation cannot reliably refresh `chitty.toml` to its newly selected source version. Resolve TASK-83 first; then implement and verify the release command against the corrected version source.

Deferred by the human (2026-11-01): not urgent; a multi-step manual release is fine for now. Dependency on TASK-83 removed to break the cycle; revisit once TASK-83 has fixed where the version lives.

Replaces the earlier scheme, including `HUMAN-6`'s comparison of `init` output, which no longer applies because versions are not chosen at release time. Earlier notes describe that scheme.

Built in the planning session as a comparison with the pipeline: 10 lines of `Makefile`, in commit `b5a1835`. Trial script against a local bare `origin`: off `main`, a dirty tree and behind `origin` each exited non-zero with a message and pushed nothing; the good path ran `make check`, pushed `main` and `v0.1.27` to the bare repository, and wrote `0.1.27` to `pending-release` under a temporary `XDG_DATA_HOME`; a repeat failed on the existing tag. The real remote and the real data directory were not touched. `mate --list` shows the target. Not tried: the real workflow, which runs on the first real release. Reviewer: do not run `make release` here, because it pushes to the real `origin`.

Reviewed: independently trialled `make release` against a local bare `origin`; verified all refusal paths, atomic branch/tag push, `pending-release`, and duplicate-tag failure. `make check`, `chitty check`, `chitty fix`, and `mate --list` pass.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
- 2026-11-01 blocked → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → blocked
- 2026-11-01 blocked → backlog
- 2026-11-04T19:22:14Z mellow-newt: changed title, priority, description, acceptance criteria, notes
- 2026-11-04T19:22:14Z mellow-newt backlog → todo
- 2026-11-04T19:32:35Z mellow-newt: wrote the plan
- 2026-11-04T19:32:35Z mellow-newt todo → doing
- 2026-11-04T19:32:36Z mellow-newt: changed notes; ticked acceptance criteria
- 2026-11-04T19:32:37Z mellow-newt doing → review
- 2026-11-04T21:58:22Z lively-vole: changed notes; ticked acceptance criteria
- 2026-11-04T21:58:22Z lively-vole review → done
- 2026-11-05T14:44:48Z vivid-wren done → archived
