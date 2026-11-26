---
title: Ticket guard refuses when branch and main copies are identical
status: todo
labels:
  - bug
priority: medium
created: 2026-11-24
---

## Description

Seen 2026-11-23 (`TASK-608`) and 2026-11-24 (echonomicon `TASK-164`): every `chitty list` failed with `ticket <ID> changed on both <branch> and main`, although `git diff main <branch> -- <ticket file>` was empty. The branch tip was a rebased copy of a commit already on `main`, so both sides had changed the file since their merge base, to the same content. The fix by hand was resetting the branch.

Cause: `changed_on_both` inside `Repo._choose_source` (`src/chitty/store.py`) calls `git.changed_since_split` in both directions, comparing each side only with the merge base.

Change: in `changed_on_both`, first return `False` when the ticket's files are identical on the two refs (one `git diff --quiet <main tip> <ref> -- <paths>`, using the `paths` it already computes), before the two merge-base checks. `ticket_source` then picks the ticket branch as it does when only that side changed, which is harmless because the copies are equal.

No property test: the cases are a fixed pair (identical, different), both listed.

Out of scope: listing tickets whose copies really differ (TASK-472).

## Acceptance Criteria

- [ ] A real-Git test: commit ticket `TASK-1` on `main`, branch `task-1`, make the same ticket edit on both `main` and `task-1` as separate commits (byte-identical files, both sides changed since the split): `chitty list` and `chitty show TASK-1` succeed and show that copy. Fails today with ``ticket `TASK-1` changed on both `task-1` and `main` ``.
- [ ] Regression tests: when the two copies differ, `changed on both` is still raised, as `tests/test_authoritative_listing.py` and `tests/test_source_copy_errors.py` expect; `tests/test_property_ticket_source.py` passes; `make check` passes.

## History

- 2026-11-24T22:21:30Z zesty-coral-newt → backlog
- 2026-11-24T22:21:31Z zesty-coral-newt: changed notes
- 2026-11-24T22:39:53Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:44Z zesty-coral-newt: changed labels
- 2026-11-26T00:23:04Z calm-ochre-quail: replaced notes; changed priority, description, acceptance criteria
- 2026-11-26T00:23:04Z calm-ochre-quail backlog → planning
- 2026-11-26T00:23:11Z calm-ochre-quail planning → cold-read
- 2026-11-26T00:24:12Z calm-ochre-quail: changed description, acceptance criteria
- 2026-11-26T00:24:12Z calm-ochre-quail cold-read → todo
