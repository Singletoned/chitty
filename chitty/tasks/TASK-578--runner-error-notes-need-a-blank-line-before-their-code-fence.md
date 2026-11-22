---
title: Runner error notes need a blank line before their code fences
status: backlog
created: 2026-11-22
---

## Description

In taidy (2026-11-22), the runner wrote a TASK-21 note `Runner error (check): check exited with status 2:` followed directly by a ```` ```text ```` fence, and `Error output:` followed directly by a ````` ````text ````` fence. Prettier requires a blank line there, so the ticket file failed the project `make check` (prettier --check) on the next run, and the runner errored the ticket again because of its own note. Fix: emit a blank line between the lead-in line and the fence. Projects can work around it with `autoformat` in `chitty.toml`, but the default output should already be valid Prettier Markdown.

## Notes

Suggestion origin: taidy

## History

- 2026-11-22T13:16:25Z friendly-jade-stoat → backlog
- 2026-11-22T13:16:25Z friendly-jade-stoat: changed notes
