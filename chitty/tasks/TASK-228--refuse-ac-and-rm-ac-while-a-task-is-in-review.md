---
title: Refuse `--ac` and `--rm-ac` while a task is in review
status: backlog
created: 2026-11-07
---

## Description

In `src/chitty/store.py:check_edit`, reject `--ac` and `--rm-ac` while the task is already in `review`, just as `--set-ac` is rejected. Check the pre-edit status, so an edit that also moves `review` to `doing` or `done` cannot change criteria; `doing` to `review` may still change them. Reject before review-note and verdict checks. Leave `--check` and `--uncheck` unchanged. Add regression tests via the CLI and the shared store path with real files in temp repositories. Scope: criterion mutations only.

## Acceptance Criteria

- [ ] Fail-first tests show `--ac` and `--rm-ac` each being accepted on a review ticket before the fix, including a combined `review` to `done` edit with a valid verdict. After the fix, each is rejected with a clear message and leaves the file unchanged; `--set-ac` remains rejected.
- [ ] Tests show criteria may still change when moving `doing` to `review`, and CLI and shared store validation agree; `make check` passes.

## Notes

Cold-read finding resolved: the refusal is the decision, not an open question; guard pre-edit review status even during a simultaneous status change. Include fail-first CLI and shared-store coverage.

## History

- 2026-11-07T10:09:05Z vivid-dormouse → backlog
- 2026-11-08T14:15:12Z eager-puffin: changed description, acceptance criteria, notes
