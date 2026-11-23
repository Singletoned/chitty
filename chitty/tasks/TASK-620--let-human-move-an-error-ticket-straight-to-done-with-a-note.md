---
title: Let `--human` move an `error` ticket straight to `done`, with a note
status: planning
created: 2026-11-23
---

## Description

When a ticket's review passed and its code reached `main`, but a landing step then set it to `error` (TASK-540, 2026-11-22: a flaky landing check after `9027093c`), there is no way for a person to finish it. `-s done` from `error` is refused with `setting status done requires -s review first` (`Repo.edit`, `src/chitty/store.py:961`). Going `error → review → done --human` is refused by the review-independence guard in `check_edit` (`store.py:1602`), because the human made the move to `review`. An agent ended up marking it done.

Decision (the person, 2026-11-23: the simplest fix): a person, with `--human`, may move a ticket from `error` straight to `done`, but must give a note with the reason. Nothing else changes: agents still cannot, and no other status gains a shortcut to `done`.

`--human` is a CLI flag (`cli.py:738`) that sets `CHITTY_ACTOR=human` for the edit; `cli.py` must stay thin, so the rule lives in `store.py`. Pass the fact to the store as a field on `Edit` (for example `human: bool`) rather than reading the environment there.

This is a small fixed set of cases (statuses × `--human` × note), so test every member rather than a property.

Out of scope: inferring that a passed review exists from Notes or `Task:` commits, and the landing behaviour itself (TASK-609).

## Acceptance Criteria

- [ ] A test in `tests/test_edit_human.py` takes a ticket in `error` in a context that requires review and runs `chitty edit <ID> -s done --human --note <reason>`; it succeeds, the ticket is `done`, the note is in Notes, and History records actor `human`. This test fails on `main` today.
- [ ] Tests cover every status except `review` and `done` as the previous status, each with and without `--human` and with and without a note: only `error` + `--human` + a non-empty note may move to `done`; every other case without review still fails with `setting status done requires -s review first`, and `error` + `--human` without a note fails with `moving error → done requires --note with the reason`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-23T10:24:18Z witty-russet-gannet → backlog
- 2026-11-23T10:24:19Z witty-russet-gannet: changed notes
- 2026-11-23T10:31:17Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:31:17Z witty-russet-gannet backlog → planning
