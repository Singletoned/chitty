---
title: Tell agents that a mistake made with Chitty is a Chitty defect to suggest
status: backlog
created: 2026-11-26
provisional: true
---

## Description

The person, 2026-11-25: "chitty is supposed to make things easy for you... anything you get wrong with chitty is chitty's fault." In one planning session the agent made several Chitty mistakes and treated each as its own slip rather than reporting it:
- It ran a ticket edit in the main checkout instead of the plan worktree (the shell had reset), so a commit landed on `main`.
- A refused `chitty edit` was followed by a separate `-s todo` that went through.
- It used `chitty note` on a plan branch and was refused; it had to know to use `chitty edit --note`.
- It passed `-d-file` to `chitty suggest` (the option is `--description-file`).
Only some of these became suggestions, and only when the person pushed.

Suggest: the general guide (`chitty guide`, shown in every repository) says, in one line, that when an agent gets something wrong while using Chitty (a wrong command, a wrong place, an easy mistake, a confusing error), it treats that as a Chitty defect and sends `chitty suggest chitty "<title>" -d "<what happened and what would have prevented it>"`, without asking. To make room, cut or shorten a line that covers less. Chitty's errors could also end with a pointer to `chitty suggest chitty` when they refuse a command, so the path is visible at the moment of failure.

## Notes

Suggestion origin: chitty

## History

- 2026-11-26T10:54:50Z calm-ochre-quail → backlog
- 2026-11-26T10:54:53Z calm-ochre-quail: changed notes
