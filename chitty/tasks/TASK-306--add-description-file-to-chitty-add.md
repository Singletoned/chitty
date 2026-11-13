---
title: Add `--description-file` to `chitty add`
status: backlog
created: 2026-11-12
---

## Description

`chitty edit` has `--description-file`, but `chitty add` has only `-d`, so a multi-line description with backticks must go through `-d "$(cat file)"`, where shell quoting is easy to get wrong. Seen 2026-11-12 creating TASK-302: `chitty add ... --description-file` failed with `No such option`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-12T21:43:30Z kind-yellow-vole → backlog
- 2026-11-12T21:43:31Z kind-yellow-vole: changed notes
