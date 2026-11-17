---
title: Accept every long text option from a file or stdin
status: planning
created: 2026-11-16
---

## Description

`--summary` has no file form, and only `--note-file` reads `-` for stdin. Every guide carries two paragraphs on escaping backticks and apostrophes in shell arguments. Give every text option of `chitty add` and `chitty edit` a `-file` form that accepts `-`, then replace the quoting advice with one line: pass text containing backticks through a file or stdin.

## History

- 2026-11-16T09:59:58Z intrepid-coral-raven → backlog
- 2026-11-16T10:38:41Z intrepid-coral-raven backlog → planning
