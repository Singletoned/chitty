---
title: Configure default models for work and review sessions
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-08
---

## Description

Allow a repository to choose persistent, independent model defaults in `chitty.toml` (or `[tool.chitty]`): `work_model = "..."` and `review_model = "..."`, optional top-level strings. Today `chitty run --mode work -- --model MODEL` and its review equivalent work (TASK-186), but an unattended `chitty run` loop cannot use two different models without supplying mode and arguments on every invocation. After selecting a ticket, `chitty run` appends `--model` and the matching configured value to its agent command, for both the default `agent_command` and named `[agent_commands]` entries. An explicit forwarded `--model VALUE` or `--model=VALUE` takes precedence for that run and must not produce a duplicate model argument. No setting means the current invocation is unchanged. Validate nonempty model strings; do not validate model names against a provider catalog. This is an agent CLI option: document that configured commands must accept `--model`, and that a model hard-coded into an agent command takes precedence over these defaults (do not append another). Update the template comment, `README.md`, and the Config and Next action and runner sections of `PLAN.md`. Do not edit this repository’s `chitty.toml` on a ticket branch. Out of scope: choosing an agent per role, provider/model discovery, or changing `chitty next`.

## Acceptance Criteria

- [ ] With a fake agent that records arguments, tests show an unqualified `chitty run` choosing `work_model` for a work ticket and `review_model` for a review ticket; both the default agent command and `--agent NAME` work, and no setting leaves arguments unchanged.
- [ ] Tests show explicit forwarded `--model VALUE` and `--model=VALUE` overriding the corresponding configured default without duplicate model arguments; a model already in the chosen agent command remains authoritative.
- [ ] Tests show blank configured model values rejected clearly, configuration in both `chitty.toml` and `[tool.chitty]` working, and `README.md`, `PLAN.md`, and the init template describing the defaults.

## History

- 2026-11-08T13:21:57Z eager-puffin → backlog
