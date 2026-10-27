---
title: Add a review status, on by default
status: done
labels:
  - cli,config
depends_on:
  - TASK-30
created: 2026-10-27
---

## Description

Completed work is reviewed by a different agent or a human before it is done, and well before merge-request time. Status order becomes backlog → todo → doing → blocked → review → done. A repo setting turns enforcement on or off.

## Acceptance Criteria

- [x] review is a status between blocked and done in every context; plain list shows it; completion includes it
- [x] Repo setting review = true | false; init writes review = true for new repos and adds it on upgrade; any other value is a config error
- [x] With review = true, doing → done (and any non-review → done) is refused with a message to set -s review; with review = false, review is optional
- [x] Nothing else is required to enter review (checklist state is not checked)
- [x] review → doing requires a --note in the same command (CLI and MCP), like blocked
- [x] Agent guide: set -s review when you think it is ready; never review a ticket you worked on; pass with -s done and a Reviewed: note; fail with -s doing and a note; out-of-scope findings become new tickets; review promptly, not at merge-request time
- [x] Tests, PLAN.md, README and AGENTS.md updated

## Plan

Trace status definitions, configuration loading/upgrades, transition enforcement, and the CLI/MCP guide. Add the review setting and shared transition rules, then cover list/completion, config validation, CLI/MCP behaviour, and documentation before running make check.

## Notes

Review failed: init upgrade used a substring check and could skip adding the top-level review setting.

Review failed: add accepted initial done status while review enforcement was enabled.

Review failed: pyproject upgrade could mistake another table’s review key for the Chitty setting.

Reviewed: independent review passed; all acceptance criteria, configuration paths, and CLI/MCP transitions are covered.

## Summary

Added the review status and review-by-default setting, with shared transition enforcement and updated guidance. Verified with make check (119 tests) and an independent review.

## History

- 2026-10-27 todo → doing
- 2026-10-27 doing → review
- 2026-10-27 review → doing
- 2026-10-27 doing → review
- 2026-10-27 review → doing
- 2026-10-27 doing → review
- 2026-10-27 review → doing
- 2026-10-27 doing → review
- 2026-10-27 review → done
