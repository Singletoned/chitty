---
title: Give `chitty note` a way to read its text from a file or stdin
status: backlog
created: 2026-11-24
---

## Description

The managed AGENTS.md block says to pass text containing backticks or apostrophes through a `-file` option with `-` and a quoted heredoc. `chitty note ID TEXT` has no such option (only `--json`), so on 2026-11-23 an agent ran `chitty note TASK-557 --file -` and got `No such option '--file'`, then had to find `chitty edit --note-file -` instead. Either accept `-` as TEXT meaning stdin, or add `--file`, or have the error point at `chitty edit ID --note-file -`.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:50Z zesty-coral-newt → backlog
- 2026-11-24T22:21:51Z zesty-coral-newt: changed notes
