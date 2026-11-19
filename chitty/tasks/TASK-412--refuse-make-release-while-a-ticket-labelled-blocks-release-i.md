---
title: Refuse `make release` while a ticket labelled `blocks-release` is open
status: planning
priority: high
created: 2026-11-19
---

## Description

On 2026-11-19 `make release` published `0.5.0` although `HUMAN-12` said not to until `TASK-331` landed. Nothing enforced it: `scripts/release_version.py` chose the minor bump by itself from `needs-minor` labels, and a human ticket cannot stop a command.

Decisions:

- `scripts/release_version.py` exits non-zero, before printing a version, when any ticket file under `chitty/` outside an `archive/` directory has the label `blocks-release` and a status other than `done`. The message names each such ticket ID and title, one per line. `make release` already stops when the script fails, before it changes `src/chitty/__init__.py`.
- Put the check in a pure function, `release_blockers(tickets) -> list[...]`, taking parsed tickets, so it can be tested without files.
- Document the label in `docs/plan/` where releases are described, and in the `Releases` paragraph of `AGENTS.md`.
- Label `TASK-331` `blocks-release` when this lands, and close `HUMAN-12` as replaced by this check.

Out of scope: blocking on tickets that exist only on other branches.

## Acceptance Criteria

- [ ] Property (Hypothesis): for any list of generated tickets with drawn statuses and labels, `release_blockers` returns exactly those with `blocks-release` whose status is not `done`, in input order
- [ ] In a temp repository with one open `blocks-release` ticket, `python scripts/release_version.py` exits non-zero, prints that ticket ID, and prints no version; with the ticket `done`, it prints the version as today. `make check` passes

## History

- 2026-11-19T10:01:36Z quick-ginger-lapwing → planning
