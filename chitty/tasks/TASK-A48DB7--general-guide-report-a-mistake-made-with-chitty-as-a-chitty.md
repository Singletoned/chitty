---
title: "General guide: report a mistake made with Chitty as a Chitty defect"
status: todo
labels:
  - untestable
owner: untestable
created: 2026-11-26
provisional: true
---

## Description

### Why

The person, 2026-11-25: "chitty is supposed to make things easy for you... anything you get wrong with chitty is chitty's fault." In one planning session an agent made four Chitty mistakes and treated each as its own slip: an edit run in the main checkout instead of the plan worktree (the shell had reset), a refused `chitty edit` followed by a separate `-s todo` that went through, `chitty note` refused on a plan branch, and `-d-file` passed to `chitty suggest` (the option is `--description-file`). Only some became suggestions, and only after the person pushed. Decided 2026-11-26: one line in the general guide; no pointer appended to errors for now.

### Change

In `src/chitty/guide.md` (the general guide, written into every repository's agent instructions), add one line after "Run `chitty --help` for the command reference.", in about this wording:

If you get something wrong using Chitty (a wrong command or place, an easy mistake, a confusing error), treat it as a Chitty defect and report it, without asking: `chitty suggest chitty "<title>" -d "<what happened; what would have prevented it>"`.

This grows a 77-word guide by about 35 words. Nothing is cut: every line there is a rule agents need in each session, and each unreported mistake repeats in later sessions. Repositories get the new line when their setup files are upgraded after it lands; nothing else is needed.

### Out of scope

Adding a `chitty suggest` pointer to refusal errors.

## History

- 2026-11-26T10:54:50Z calm-ochre-quail → backlog
- 2026-11-26T10:54:53Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:19Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:19Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:12:30Z calm-ochre-quail: replaced notes; changed title, labels, owner, description
- 2026-11-26T11:12:30Z calm-ochre-quail to-plan → todo
- 2026-11-26T11:12:42Z calm-ochre-quail: changed description
