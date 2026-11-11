---
title: Guide agents through setting up chitty run
status: done
priority: medium
created: 2026-11-09
---

## Description

Add a focused `chitty guide setup` page for a coding agent helping a person enable `chitty run`. Explain how to initialize from the main checkout and edit the existing repository-root `chitty.toml`, or `[tool.chitty]` in the root `pyproject.toml` when that is the chosen config; never create both. Cover `autocommit`, `setup`, `check`, and a default `agent_command` or a `[agent_commands]` entry chosen with `chitty run --agent NAME`. Each selected command needs both `{mode}` and `{id}`, or `{prompt}`. Explain agent integration and deliberately trying a real ticket. Improve `chitty guide --help` so it lists the available guides and concrete usage examples, including the general `chitty guide` and new setup guide. Keep this useful for new and existing repositories; do not modify configuration automatically or add a wizard.

## Acceptance Criteria

- [x] `chitty guide setup` works outside a repository, names the prerequisites and exact config location, and explains main-checkout versus ticket-worktree changes and how to verify the setup. `chitty guide --help` identifies available guides and shows commands for general, setup and ticket-specific guidance.
- [x] Dedicated guide tests fail before implementation and pass afterward; `README.md` and `PLAN.md` document the new guide; `make check` passes.

## Plan

Add a packaged setup role, expose it in role dispatch without allowing ticket IDs, and improve the existing guide command help. Add fail-first dedicated CLI tests for the setup page and help examples. Link the page from README and document the role in PLAN. Run make format and make check, inspect tool changes, commit implementation, then hand off for review.

## Notes

Read-only cold read clarified that there are two mutually exclusive config locations and that named agent commands still require placeholders; both are included in the description.

Fail-first: new tests/test_guide_setup.py produced 8 assertion failures before implementation: setup was an unknown role, the guide help omitted examples, and setup with a ticket ID was not handled. After adding the setup guide and help, 15 focused tests passed. make format && make check passed after merging current main (406 Python tests and Node tests); chitty fix reported only existing warnings in unrelated ticket files. No version, managed agent block or repository configuration changed on this branch.

Reviewed: verified the setup guide and help outside a repository, inspected dispatch, documentation and tests, and reproduced eight failures against main. make format && make check passed (406 Python tests and Node tests).
1: pass - Setup guide and help cover the requested instructions and examples.
2: pass - Dedicated tests fail against main and pass on this branch; documentation and full checks pass.

## Summary

Handoff: chitty guide setup provides main-checkout configuration instructions for new and existing repositories, Pi or other agents, and a real-run verification path. chitty guide --help lists roles and examples and shows optional ID correctly. Verified fail-first tests, focused guide tests, and full checks after main integration. No follow-ups.

## History

- 2026-11-09T11:51:54Z eager-puffin → todo
- 2026-11-09T11:53:11Z eager-puffin: changed description, notes
- 2026-11-09T11:53:37Z eager-puffin: changed description, acceptance criteria; wrote the plan
- 2026-11-09T11:53:37Z eager-puffin todo → doing
- 2026-11-09T12:00:51Z eager-puffin: changed notes, summary; ticked acceptance criteria
- 2026-11-09T12:00:51Z eager-puffin doing → review
- 2026-11-09T12:35:22Z witty-raven: changed notes; ticked acceptance criteria
- 2026-11-09T12:35:22Z witty-raven review → done
- 2026-11-11T10:18:03Z vivid-yellowhammer: changed parent
