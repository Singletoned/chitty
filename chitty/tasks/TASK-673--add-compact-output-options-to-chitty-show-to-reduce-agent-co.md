---
title: Add compact output options to `chitty show` to reduce agent context
status: backlog
labels:
  - duplicate
created: 2026-11-24
---

## Description

When inspecting tickets with long runner/review logs (for example, `chitty show CIRCUIT-106` in `circuitry` produced 18,415 bytes), `chitty show` dumps the entire `## Notes` and `## History` sections by default. In tool-output-capped environments, that truncates the middle of the output and wastes thousands of tokens when an agent only needs the current `Description`, `Acceptance Criteria`, `Plan`, and `Summary` (or the latest notes).

Adding a compact option such as `--brief` / `--no-history` / `--latest-notes N` (or omitting `## History` unless `--full` is passed) would noticeably reduce agent context consumption when reading tickets.

## Notes

Suggestion origin: circuitry

Duplicate of BACKLOG-54277329 (compact output for inspection commands); the evidence is recorded there.

## History

- 2026-11-24T22:21:36Z zesty-coral-newt → backlog
- 2026-11-24T22:21:37Z zesty-coral-newt: changed notes
- 2026-11-24T22:40:11Z zesty-coral-newt: changed labels, notes
