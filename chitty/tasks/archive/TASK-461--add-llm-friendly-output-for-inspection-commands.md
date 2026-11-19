---
title: Add `--llm-friendly` output for inspection commands
status: backlog
created: 2026-11-19
---

## Description

Problem: Chitty output is often consumed by coding agents, but `chitty list` does not accept `--llm-friendly`, while this environment provides compact read-only output modes for commands such as `git`, `ls`, `grep`, `find`, and `rg`. A mistaken `chitty list --llm-friendly` currently exits with `Error: No such option: --llm-friendly`, forcing agents to guess which output mode is safe and concise.\n\nProposal: add a consistent `--llm-friendly` option to read-only inspection commands, initially `chitty list`, `chitty show`, `chitty inbox`, and perhaps `chitty path` if useful. It should preserve the same information and ordering as normal output while reducing tokens: one stable record per task or suggestion, compact status/priority/labels, no decorative prose, no redundant headings, and deterministic truncation or field selection. It should be script-readable but remain human-readable text; do not make it JSON or change the default output. For commands already supporting `--json`, document that JSON remains the machine-contract format and `--llm-friendly` is the compact text format.\n\nPlease define the supported command set, exact formatting, ordering, truncation rules, exit behavior, and tests for stable output. Consider a shared formatter rather than separate ad hoc flags. Evidence: on 2026-11-13, `chitty list --llm-friendly` was attempted during ticket planning and failed at option parsing.

## Notes

Suggestion origin: taidy

Archived as covered by `BACKLOG-54277329`.

## History

- 2026-11-19T20:55:37Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:38Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:47Z sunny-white-dormouse: changed notes
- 2026-11-19T20:57:50Z sunny-white-dormouse backlog → archived
