---
title: Accept every long text option of add, edit and suggest from a file or stdin
status: planning
created: 2026-11-16
---

## Description

`--summary` has no file form, and only `--note-file` reads `-` for stdin. Every guide carries two paragraphs on escaping backticks and apostrophes in shell arguments. Give every text option of `chitty add`, `chitty edit` and `chitty suggest` (which has only `-d`, so long suggestions go through `-d "$(cat file)"`, seen 2026-11-17) a `-file` form that accepts `-`, then replace the quoting advice with one line: pass text containing backticks through a file or stdin.

## History

- 2026-11-16T09:59:58Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:41Z intrepid-coral-raven backlog → planning
- 2026-11-17T17:52:25Z kind-umber-toad: changed title, description
