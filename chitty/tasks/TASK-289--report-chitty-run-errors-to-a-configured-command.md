---
title: Report `chitty run` errors to a configured command
status: backlog
created: 2026-11-11
---

## Description

- Errors from `chitty run --loop` show only in its terminal, and are easy to miss.
- Add an optional root setting `report_error`, a command like `agent_command`. When `chitty run` exits with a Chitty error, it runs this command with `{message}` (the error text) and `{context}` (JSON with project, ticket, mode, actor and worktree, where known), then exits as before. A failing report command prints a warning and does not hide the original error.
- This repository sets `report_error = "sump capture chitty --message {message} --context-json {context}"`, on `main`. TASK-256 later reads errors back from Sump.
- Document it in `README.md` and `PLAN.md` "Config".

## Acceptance Criteria

- [ ] With `report_error` set to a script that writes its arguments to a file, a `chitty run` that fails with a Chitty error leaves the message and a JSON context naming the ticket in that file, and still exits non-zero. It fails today.
- [ ] Without `report_error`, behaviour is unchanged.

## History

- 2026-11-11T16:17:52Z vivid-yellowhammer → backlog
