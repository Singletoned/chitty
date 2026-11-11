---
title: Report `chitty run` errors to a configured command
status: todo
created: 2026-11-11
---

## Description

- Errors from `chitty run --loop` show only in its terminal, and are easy to miss.
- Add an optional root setting `error_reporter`, a command parsed like `agent_command` (split first, then each word substituted in one pass, so a message containing spaces, quotes or `{context}` stays one argument). When `chitty run` fails with a Chitty error, it runs this command with `{message}` (the error text) and `{context}` (JSON with `actor`, and `project`, `ticket` and `mode` once known), then exits as before. Hook it in `run()` in `src/chitty/run.py`, where the config and ticket are known.
- Not reported: an empty queue (`NoNextTicket`), Ctrl-C (`RunInterrupted`), and config errors before the config loads. Under `--loop`, each failing child reports once and the parent does not.
- A failing reporter prints a warning and does not hide the original error.
- After this lands, the planner sets `error_reporter = "sump capture chitty --message {message} --context-json {context}"` on `main`; the branch leaves `chitty.toml` alone. TASK-256 later reads errors back from Sump.
- Document it in `README.md` and `PLAN.md` "Config".

## Acceptance Criteria

- [ ] With `error_reporter` set to a script that writes its arguments to a file, a `chitty run` whose agent command exits 1 leaves the message and a JSON context naming the ticket in that file, and still exits non-zero. It fails today.
- [ ] Without `error_reporter`, behaviour is unchanged; with it, a successful run and an empty queue run no reporter.
- [ ] A reporter that exits non-zero prints a warning, and `chitty run` still fails with the agent's error.

## Notes

Possible starting point: `git diff main...refs/cold-read/TASK-289/1`. Check it against the current criteria; do not trust it.

## History

- 2026-11-11T16:17:52Z vivid-yellowhammer → backlog
- 2026-11-11T18:50:21Z vivid-yellowhammer: changed description
- 2026-11-11T18:50:28Z vivid-yellowhammer: changed description
- 2026-11-11T18:50:29Z vivid-yellowhammer: changed acceptance criteria
- 2026-11-11T18:50:57Z vivid-yellowhammer backlog → cold-read
- 2026-11-11T18:54:56Z vivid-yellowhammer: changed description
- 2026-11-11T18:54:58Z vivid-yellowhammer: changed acceptance criteria, notes
- 2026-11-11T18:54:58Z vivid-yellowhammer cold-read → todo
