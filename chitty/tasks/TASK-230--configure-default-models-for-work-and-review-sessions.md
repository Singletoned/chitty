---
title: Configure default models for work and review sessions
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-08
---

## Description

Allow a repository to choose persistent, independent model defaults in `chitty.toml` (or `[tool.chitty]`): `work_model = "..."` and `review_model = "..."`, optional top-level strings. Today `chitty run --mode work -- --model MODEL` and its review equivalent work (TASK-186), but an unattended `chitty run` loop cannot use two different models without supplying mode and arguments on every invocation. After selecting a ticket, `chitty run` appends `--model` and the matching configured value to its agent command, for both the default `agent_command` and named `[agent_commands]` entries. Append a role default only when neither the selected agent command nor the forwarded agent arguments after `--` already contain `--model VALUE` or `--model=VALUE`; do not rewrite existing arguments or introduce a duplicate. Thus an explicitly forwarded or command-embedded model takes precedence over the role default, and existing behavior is unchanged if both already specify models. No setting means the current invocation is unchanged. Validate nonempty model strings; do not validate model names against a provider catalog. This is an agent CLI option, not a Chitty `--model` flag: document that a command receiving a role default must accept `--model`. Add commented examples to the initial `chitty.toml` template and `chitty init` upgrade comments. In `chitty.toml`, put them before the first table header, as root keys; in `pyproject.toml`, put them after `[tool.chitty]` and before the next table header, as keys directly in that table. Never place them in `[agent_commands]`. Update `README.md` and the Config and Next action and runner sections of `PLAN.md`. Do not edit this repository’s `chitty.toml` on a ticket branch. Out of scope: choosing an agent per role, provider/model discovery, or changing `chitty next`.

## Acceptance Criteria

- [ ] With a fake agent that records arguments, tests show an unqualified `chitty run` choosing `work_model` for a work ticket and `review_model` for a review ticket; both the default agent command and `--agent NAME` work, and no setting leaves arguments unchanged.
- [ ] Tests show forwarded `--model VALUE` and `--model=VALUE` each suppressing the role default, and a model in the selected agent command suppressing it too; existing behavior is unchanged when both sources already specify a model.
- [ ] Tests show blank configured model values rejected clearly, configuration in both `chitty.toml` and `[tool.chitty]` working, and `README.md`, `PLAN.md`, and the init template describing the defaults.

## Notes

Read-only cold read: the first draft left precedence ambiguous when a command already had `--model`, and did not identify where `chitty init` inserts comments. Fixed the description and criterion 2: existing model arguments suppress the role default without rewriting them, and commented config examples belong before table headers. A fresh implementing cold read with tests and `make check` is still needed before promotion from backlog.

Second read-only cold read found a TOML placement contradiction: pyproject examples must be placed after `[tool.chitty]`, not before the first table header. Corrected the description. Require a pyproject init test that checks placement and uncommented parsing. Implementing cold read still pending.

## History

- 2026-11-08T13:21:57Z eager-puffin → backlog
- 2026-11-08T13:23:28Z eager-puffin: changed description, acceptance criteria
- 2026-11-08T13:23:56Z eager-puffin: changed notes
- 2026-11-08T14:15:33Z eager-puffin: changed description
- 2026-11-08T14:15:35Z eager-puffin: changed notes
