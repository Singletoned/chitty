---
title: Check `claude` usage logging against a real session
status: backlog
priority: medium
owner: human
depends_on:
  - TASK-155
  - TASK-157
parent: TASK-106
created: 2026-11-04
---

## Description

The planning session adds the `--settings` part from `TASK-157` to this repository's `claude` entry, and shows it in `README.md`, written as a TOML basic string with `\"` inside shell single quotes, which is the form checked to survive `shlex.split`. The human then runs `chitty run --agent claude` from an ordinary shell, because a worker cannot start `claude`, and the planning session compares the log line with the session's transcript and subagent transcripts, per model, counting each `message.id` once. Check that `SessionEnd` fires under `-p`, and that `claude` exits normally afterwards. A difference of more than 5% in any model's tokens means a call is missing, so say what is missing rather than adjusting for it. If the hook does not fire, record that and file a ticket: the hook's design would need rethinking.

## Acceptance Criteria

- [ ] A note records the real log line, the transcripts' sum and any difference, that the hook fired under `-p`, and that `claude` exited normally
- [ ] `README.md` shows the `--settings` part of the `claude` entry, and this repository's entry uses it

## Notes

Cold read with `TASK-157`, 2026-11-04. Fixed: per-model comparison, subagent transcripts, what happens if the hook does not fire, and it now holds the connecting and documentation from `TASK-157`.

## History

- 2026-11-04T18:01:19Z mellow-newt → backlog
- 2026-11-04T18:03:11Z mellow-newt: changed description, acceptance criteria, notes
