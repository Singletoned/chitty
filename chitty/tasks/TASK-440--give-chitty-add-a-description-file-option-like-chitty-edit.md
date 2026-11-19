---
title: Give `chitty add` a `--description-file` option like `chitty edit`
status: backlog
created: 2026-11-19
---

## Description

In circuitry on 2026-11-13, `chitty add ... --description-file FILE` failed with "No such option", while `chitty edit` accepts `--description-file` and `--plan-file`. Long ticket descriptions with backticks then have to go through `-d "$(cat FILE)"`, which is easy to get wrong with shell quoting. Add `--description-file` (and `--plan-file` if add takes a plan) to `add` for parity with `edit`.

## Notes

Suggestion origin: circuitry

Archived as covered by `TASK-347`.

## History

- 2026-11-19T20:55:12Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:13Z sunny-white-dormouse: changed notes
- 2026-11-19T20:56:28Z sunny-white-dormouse: changed notes
