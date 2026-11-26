---
title: "General guide: report a mistake made with Chitty as a Chitty defect"
status: done
labels:
  - untestable
owner: human
created: 2026-11-26
moved_from: TASK-A48DB7
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

## Plan

Add one concise line to `src/chitty/guide.md` after the `chitty --help` line instructing agents to treat any Chitty mistake as a Chitty defect and report it without asking via `chitty suggest chitty`. Update `tests/fixtures/guide-runner-expected.md` to match while leaving `AGENTS.md` untouched. Verify with `make check` via `chitty edit -s review`.

## Notes

Reviewed: diff of `main...task-a48db7` adds one line after "Run `chitty --help` for the command reference." in `src/chitty/guide.md` and the same line in `tests/fixtures/guide-runner-expected.md`; `AGENTS.md` and the managed block are untouched.
1: pass - the line treats any mistake made with Chitty as a Chitty defect, says to report it without asking, and gives the `chitty suggest chitty` command (34 words, shorter than the draft).
Limit: `chitty suggest chitty` works only where the Chitty repo has registered its inbox; with an empty `XDG_DATA_HOME` it exits 1 with "unknown project 'chitty'; use --create". The person accepted this on 2026-11-26, because Chitty's users are currently on that machine.

## Summary

Added one concise line (34 words, down from 39 in the ticket draft) to `src/chitty/guide.md` after `Run `chitty --help` for the command reference.`:

Treat anything you get wrong with Chitty (wrong command or place, easy slip, confusing error) as a Chitty defect; report it without asking: `chitty suggest chitty "<title>" -d "<what happened; what would have prevented it>"`.

Updated `tests/fixtures/guide-runner-expected.md` to match and left `AGENTS.md` untouched.

Branch `task-a48db7` (worktree `.worktrees/task-a48db7`). `make check` passed via `chitty edit -s review`.

## History

- 2026-11-26T10:54:50Z calm-ochre-quail → backlog
- 2026-11-26T10:54:53Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:19Z calm-ochre-quail: changed notes
- 2026-11-26T11:11:19Z calm-ochre-quail backlog → to-plan
- 2026-11-26T11:12:30Z calm-ochre-quail: replaced notes; changed title, labels, owner, description
- 2026-11-26T11:12:30Z calm-ochre-quail to-plan → todo
- 2026-11-26T11:12:42Z calm-ochre-quail: changed description
- 2026-11-26T18:17:42Z calm-russet-badger: wrote the plan
- 2026-11-26T18:17:42Z calm-russet-badger todo → doing
- 2026-11-26T18:34:17Z calm-russet-badger: changed owner, summary
- 2026-11-26T18:34:17Z calm-russet-badger doing → review
- 2026-11-26T20:07:51Z intrepid-russet-falcon: changed notes
- 2026-11-26T20:07:51Z intrepid-russet-falcon review → done
- 2026-11-26T20:30:10Z intrepid-russet-falcon: renumbered from TASK-A48DB7
