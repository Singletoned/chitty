---
title: Configure default models for work and review sessions
status: done
priority: medium
parent: TASK-106
created: 2026-11-08
---

## Description

Allow a repository to choose persistent, independent model defaults in `chitty.toml` (or `[tool.chitty]`): `work_model = "..."` and `review_model = "..."`, optional top-level strings. Today `chitty run --mode work -- --model MODEL` and its review equivalent work (TASK-186), but an unattended `chitty run` loop cannot use two different models without supplying mode and arguments on every invocation. After selecting a ticket, `chitty run` appends `--model` and the matching configured value to its agent command, for both the default `agent_command` and named `[agent_commands]` entries. Append a role default only when neither the selected agent command nor the forwarded agent arguments after `--` already contain `--model VALUE` or `--model=VALUE`; do not rewrite existing arguments or introduce a duplicate. Thus an explicitly forwarded or command-embedded model takes precedence over the role default, and existing behavior is unchanged if both already specify models. No setting means the current invocation is unchanged. Validate nonempty model strings; do not validate model names against a provider catalog. This is an agent CLI option, not a Chitty `--model` flag: document that a command receiving a role default must accept `--model`. Add commented examples to the initial `chitty.toml` template and `chitty init` upgrade comments. In `chitty.toml`, put them before the first table header, as root keys; in `pyproject.toml`, put them after `[tool.chitty]` and before the next table header, as keys directly in that table. Never place them in `[agent_commands]`. Update `README.md` and the Config and Next action and runner sections of `PLAN.md`. Do not edit this repository’s `chitty.toml` on a ticket branch. Out of scope: choosing an agent per role, provider/model discovery, or changing `chitty next`.

## Acceptance Criteria

- [x] With a fake agent that records arguments, tests show an unqualified `chitty run` choosing `work_model` for a work ticket and `review_model` for a review ticket; both the default agent command and `--agent NAME` work, and no setting leaves arguments unchanged.
- [x] Tests show forwarded `--model VALUE` and `--model=VALUE` each suppressing the role default, and a model in the selected agent command suppressing it too; existing behavior is unchanged when both sources already specify a model.
- [x] Tests show blank configured model values rejected clearly, configuration in both `chitty.toml` and `[tool.chitty]` working, and `README.md`, `PLAN.md`, and the init template describing the defaults. An init upgrade puts pyproject comments inside `[tool.chitty]` even when another table has a `work_model` key; uncommenting them parses as Chitty settings.

## Plan

Port and independently verify the cold-read candidate against the current ticket: add validated role model settings and template/init comments, append the selected role default only when command and forwarded args lack a model, and update README/PLAN. First run the focused regression tests against the unfixed branch to confirm failure, then apply the candidate, run focused tests, format and full checks, inspect the final diff, and complete the ticket with verification notes.

## Notes

Read-only cold read: the first draft left precedence ambiguous when a command already had `--model`, and did not identify where `chitty init` inserts comments. Fixed the description and criterion 2: existing model arguments suppress the role default without rewriting them, and commented config examples belong before table headers. A fresh implementing cold read with tests and `make check` is still needed before promotion from backlog.

Second read-only cold read found a TOML placement contradiction: pyproject examples must be placed after `[tool.chitty]`, not before the first table header. Corrected the description. Require a pyproject init test that checks placement and uncommented parsing. Implementing cold read still pending.

Repeat cold read found a cross-table false-positive in init comment insertion when `[tool.other]` already has `work_model`. Added a failing regression case, and the candidate now checks only the Chitty settings section. Recheck before promotion.

Implementing cold read completed after the read-only findings and a repeat read: unqualified work/review model test failed against the unfixed runner (`default work TASK-1` instead of `--model work-model`); blank-model, override, and cross-table init tests also failed before their fixes. The final candidate passes the focused six tests and full `make check` (383 Python tests and Node tests). No remaining serious finding. Kept the implementation at `refs/cold-read/TASK-230/1`; use `git diff main...refs/cold-read/TASK-230/1` as a possible starting point, verifying it against the current criteria. The earlier note saying implementing cold read was pending is superseded.

Regression evidence: the new focused test suite failed before implementation (wrong unqualified model args, blank values accepted, missing init/template examples); it passes after implementation. Verification: make format && make check passed (384 Python tests plus Node tests, ruff and pyright). chitty fix completed with only pre-existing Markdown warnings in other task files. Implemented role defaults for default/named commands, model precedence, validation, and init placement. Commit: 7a96c2e (Task: TASK-230).

Reviewed: make format && make check passed: 385 Python tests, Node tests, ruff and pyright.
1: pass - Fake agent tests cover unqualified work and review, named and default agents, and absent settings.
2: pass - Fake agent tests cover forwarded and command models and combined precedence.
3: pass - Tests cover validation, both config formats, template and pyproject upgrade placement; README and PLAN document defaults.

## Summary

Implemented and committed as 7a96c2e. Handoff: role-specific work_model/review_model defaults are supported, documented, and covered by regression tests for both config formats, named commands, forwarded overrides, and init comment placement. Verification: focused tests and make format && make check passed. Follow-up: none; chitty fix surfaced pre-existing warnings in unrelated task files.

## History

- 2026-11-08T13:21:57Z eager-puffin → backlog
- 2026-11-08T13:23:28Z eager-puffin: changed description, acceptance criteria
- 2026-11-08T13:23:56Z eager-puffin: changed notes
- 2026-11-08T14:15:33Z eager-puffin: changed description
- 2026-11-08T14:15:35Z eager-puffin: changed notes
- 2026-11-08T14:51:01Z eager-puffin: changed acceptance criteria, notes
- 2026-11-08T14:55:45Z eager-puffin: changed notes
- 2026-11-08T14:55:46Z eager-puffin backlog → todo
- 2026-11-08T17:13:34Z upbeat-kestrel todo → doing
- 2026-11-08T17:13:56Z upbeat-kestrel: wrote the plan
- 2026-11-08T17:15:48Z upbeat-kestrel: changed notes, summary; ticked acceptance criteria
- 2026-11-08T17:15:51Z upbeat-kestrel doing → review
- 2026-11-08T17:20:30Z calm-zander: changed notes; ticked acceptance criteria
- 2026-11-08T17:20:30Z calm-zander review → done
