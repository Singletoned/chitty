---
title: Fail `make check` when a setup change has no version bump
status: doing
priority: medium
parent: TASK-106
created: 2026-11-04
---

## Description

Accepted by the human from the `TASK-108` retro, proposal 1. A missed or lost `__version__` bump caused failures on `TASK-93`, `TASK-104` and `TASK-126`, and two tickets bumping to the same version merge silently, so repositories never learn about the later change.

Add `scripts/check_version_bump.py`, using only Git and the standard library, as a step in `make check`:

1. If `refs/heads/main` does not exist, print a notice to stderr and pass. The release workflow checks out one commit of a tag with no `main`, and this is a guard on branches. On `main` itself, it passes too.
2. Decide what changed by comparing the working tree with the merge-base of `HEAD` and `main`, so a branch that is merely behind `main` is not blamed for files it did not touch. The watched files are `src/chitty/guide.md`, `src/chitty/integrations/pi/chitty.ts`, everything under `src/chitty/roles/`, and the text of the `INITIAL_CONFIG` string in `src/chitty/config.py`, found with a regular expression, rather than the whole of `config.py`, which changes for other reasons. A file added or removed counts as changed.
3. If any changed, `__version__` must be above the one in `main`'s tip, not the merge-base, so two tickets taking the same version are caught once the second is behind. Compare numerically, part by part. A version that is not dotted integers fails loudly.

Failure names the changed files and both versions.

## Acceptance Criteria

- [ ] Tests in temporary Git repositories show each watched change failing without a higher version and passing with one, the same version as `main`'s tip failing, `0.1.10` counting as above `0.1.9`, and an unrelated `config.py` change passing
- [ ] Tests show a branch behind `main` that changed nothing passing, running on `main` passing, and a `--depth 1` clone at a tag with no `main` passing with a notice
- [ ] `make check` runs it

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: my criterion about the release workflow was false as written, because its checkout has no `main`; so a missing `main` passes with a notice. Comparing with `main`'s tip alone would blame a branch for files it never touched, so what changed comes from the merge-base and the version from the tip. Also the script's location, the template's extraction and `roles/`, which exists now. No `__version__` bump is needed: the script reaches no other repository.

## History

- 2026-11-04T20:45:25Z mellow-newt → backlog
- 2026-11-04T20:47:38Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T20:47:39Z mellow-newt backlog → todo
- 2026-11-05T22:22:37Z jolly-kestrel todo → doing
