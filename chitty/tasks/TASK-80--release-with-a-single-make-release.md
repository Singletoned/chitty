---
title: Release with a single `make release`
status: todo
priority: high
created: 2026-11-01
---

## Description

Add `make release`: tag the version already in `src/chitty/__init__.py` and push it, so `release.yml` publishes it. It refuses unless on `main`, with a clean tree, with `origin/main` contained in `HEAD`, and with `make check` passing. Pushing the branch and tag is atomic, and an existing tag fails. After the push it writes the version to `$XDG_DATA_HOME/chitty/pending-release`, which says a release is on its way, for the upgrade alert.

Rewritten 2026-11-04 at the human's prompting: this waited since 2026-11-01 while the ticket grew a scheme for choosing minor or patch. `__version__` is already bumped in each change that needs it, so releasing only has to tag it, and the per-change rule stays.

## Acceptance Criteria

- [ ] A trial with a local bare `origin` shows `make release` refusing off `main`, with a dirty tree and when behind `origin/main`, and otherwise pushing `main` and the tag and writing `pending-release`
- [ ] `AGENTS.md` describes releasing with `make release`, and `mate --list` shows the target

## Plan

Inspect the existing Makefile, release workflow, tags, and setup output. Add a guarded `mate release` target that determines the required version bump from setup changes, updates generated files, verifies checks, commits, tags, and pushes. Add hermetic tests for bump selection and guards; update release documentation; run `make check` and target tests before requesting review.

## Notes

Blocked pending HUMAN-6: the specified `init` comparison always changes `chitty_version`, so it cannot distinguish patch from minor. Implementation would encode an unintended always-minor policy.

Unblocked: HUMAN-6 decided that the comparison ignores `chitty_version` (criterion rewritten, now number 4).

Blocked on TASK-83: `chitty init` reads the installed package metadata version, so release automation cannot reliably refresh `chitty.toml` to its newly selected source version. Resolve TASK-83 first; then implement and verify the release command against the corrected version source.

Deferred by the human (2026-11-01): not urgent; a multi-step manual release is fine for now. Dependency on TASK-83 removed to break the cycle; revisit once TASK-83 has fixed where the version lives.

Replaces the earlier scheme, including `HUMAN-6`'s comparison of `init` output, which no longer applies because versions are not chosen at release time. Earlier notes describe that scheme.

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
