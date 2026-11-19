---
title: Show the 🔗 dependency glyph in `chitty list`, including `planning` and `cold-read` tickets
status: backlog
parent: TASK-70
created: 2026-11-19
---

## Description

Seen 2026-11-19: `TASK-450` is in `planning` with `depends_on: TASK-426`, but `chitty list` shows nothing in its glyph column, so a planner cannot see that it waits on another ticket. The column is `skip_reason` (`src/chitty/selection.py`), which explains why `chitty next`/`chitty run` would skip a ticket, and checks dependencies only for `todo` (`if fact.status != "todo": return None`). Planning tickets are never picked, so they get no reason.

Direction: the dependency glyph changes from 🔒 to 🔗 everywhere it is shown (owner decision 2026-11-19, recorded on `TASK-70`: one code point, always two columns wide), and `chitty list` shows `🔗 waits on <IDs>` for a `planning` or `cold-read` ticket with an unfinished dependency, as it does for `todo`. Update tests, `README.md` and `docs/plan/` text that show 🔒 (`git grep -n 🔒`). Decide when planning whether this goes in `skip_reason` (it would then also appear in `--json` `skipped`, which is about selection) or in the list code only; the second keeps `skip_reason` about selection. Owner, running and human glyphs keep their current precedence. A slice of `TASK-70` criterion 1 (mark tasks with `depends_on` as queued), which covers every status and `show` as well; the glyph choice is recorded there.

## History

- 2026-11-19T21:45:57Z sunny-white-dormouse → backlog
- 2026-11-19T21:56:42Z sunny-white-dormouse: changed title, description
