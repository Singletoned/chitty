---
title: Give `chitty add` the `--description-file` option that `chitty edit` has
status: backlog
created: 2026-11-19
---

## Description

Agents planning tickets write long descriptions to a file and pass them in. `chitty edit` accepts `--description-file FILENAME`, but `chitty add` does not (`Error: No such option --description-file`), so agents fall back to `-d "$(cat file)"`, which breaks on quoting. A planning agent hit this twice in one session on 2026-11-19 (creating TASK-426 and TASK-427). Adding the same option to `add` (and to the MCP add tool if it takes a description) keeps the two commands consistent.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:06Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:07Z sunny-white-dormouse: changed notes
