---
title: Add `make audit` with bandit
status: backlog
parent: TASK-290
created: 2026-11-11
---

## Description

- Add bandit as a dev dependency and `scripts/audit.py`, run by a new `make audit` target (`## run security and test-quality tools on main; suggest tickets`).
- It runs `bandit -r src -f json`, and for each (rule, file) pair with findings sends `chitty suggest . "Audit: bandit <rule> in <file>"`, with the findings' lines and messages as the description. A pair whose title is already a ticket title, open or archived, is skipped.
- Exit 0 when it ran, whether or not it found anything; non-zero only if a tool fails to run.

## Acceptance Criteria

- [ ] A test runs the audit on a temporary repository holding a file with one bandit finding: one suggestion arrives, titled with the rule and file. Running it again sends none. It fails today.

## History

- 2026-11-11T16:18:23Z vivid-yellowhammer → backlog
