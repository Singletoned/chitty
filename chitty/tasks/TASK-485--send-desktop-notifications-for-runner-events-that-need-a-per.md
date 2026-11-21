---
title: Send desktop notifications for runner events that need a person
status: backlog
created: 2026-11-21
---

## Description

On 2026-11-20 both `chitty run --loop` processes exited at 17:48 and nobody noticed until the human happened to look at the terminals; an agent watching ticket status every 30 minutes missed it too. Suggest an optional notification hook in `chitty run`, configured in `chitty.toml` (for example `notify = "osascript -e 'display notification \"{message}\" with title \"chitty\"'"` on macOS, `notify-send` on Linux), called for: a loop stopping, and why; a ticket going to `error` or `blocked`; a ticket returned to `planning`; a ticket assigned to `human`; a release failing. Keep it one command template rather than per-platform code, so it can also post to Slack or write a file. A related suggestion filed the same day asks for a loud signal when a loop stops; this generalises it.

## Notes

Suggestion origin: chitty

## History

- 2026-11-21T07:57:46Z nimble-umber-gannet → backlog
- 2026-11-21T07:57:47Z nimble-umber-gannet: changed notes
