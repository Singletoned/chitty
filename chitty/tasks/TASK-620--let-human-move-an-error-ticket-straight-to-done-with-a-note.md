---
title: Let `--human` move an `error` ticket straight to `done`, with a note
status: cold-read
created: 2026-11-23
---

## Description

When a ticket's review passed and its code reached `main`, but a landing step then set it to `error` (TASK-540, 2026-11-22: a flaky landing check after `9027093c`), there is no way for a person to finish it. `-s done` from `error` is refused with `setting status done requires -s review first` (`Repo.edit`, the raise at about `src/chitty/store.py:967`). Going `error → review → done --human` is refused by the review-independence guard in `check_edit` (`store.py:1602`), because the human made the move to `review`. An agent ended up marking it done.

Decision (the person, 2026-11-23: the simplest fix): a person, with `--human`, may move a ticket from `error` straight to `done`, but must give a note with the reason. Nothing else changes: agents still cannot, and no other status gains a shortcut to `done`.

`--human` is a CLI flag (`cli.py:738`) that sets `CHITTY_ACTOR=human` for the edit; `cli.py` must stay thin, so the rule lives in `store.py`. Pass the fact to the store as a field on `Edit` (`src/chitty/store.py:150`), for example `human: bool`, set only by `edit` in `cli.py` (`human=human_edit`), rather than reading the environment there. MCP never sets it, so MCP edits stay refused.

A note means `--note` or `--note-file` text that is not empty after `strip()`, the same rule as the move to `planning` (`check_edit`); `--set-notes` does not count. Set up tests with `chitty edit <ID> -s error` directly (no `chitty run` needed), on a `TASK-` ticket in the main checkout: `tests/support.py` uses `workflow = "runner"`, so `tasks` requires review, while `human` does not.

This is a small fixed set of cases (statuses × `--human` × note), so test every member rather than a property.

Out of scope: inferring that a passed review exists from Notes or `Task:` commits, and the landing behaviour itself (TASK-609).

## Acceptance Criteria

- [ ] A test in `tests/test_edit_human.py` takes a ticket in `error` in a context that requires review and runs `chitty edit <ID> -s done --human --note <reason>`; it succeeds, the ticket is `done`, the note is in Notes, and History records actor `human`. This test fails on `main` today.
- [ ] Tests cover every previous status other than `review` and `done` (`backlog`, `planning`, `cold-read`, `todo`, `doing`, `blocked`, `error`), each with and without `--human` and with and without a note. Only `error` + `--human` + a note moves to `done`. `error` + `--human` without a note (including a whitespace-only `--note`) fails with `moving error → done requires --note with the reason`. Every other case fails with `setting status done requires -s review first`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-23T10:24:18Z witty-russet-gannet → backlog
- 2026-11-23T10:24:19Z witty-russet-gannet: changed notes
- 2026-11-23T10:31:17Z witty-russet-gannet: changed title, description, acceptance criteria
- 2026-11-23T10:31:17Z witty-russet-gannet backlog → planning
- 2026-11-23T10:31:32Z witty-russet-gannet planning → cold-read
- 2026-11-23T10:33:05Z witty-russet-gannet: changed description, acceptance criteria
- 2026-11-23T10:33:05Z witty-russet-gannet cold-read → planning
- 2026-11-23T10:33:09Z witty-russet-gannet planning → cold-read
