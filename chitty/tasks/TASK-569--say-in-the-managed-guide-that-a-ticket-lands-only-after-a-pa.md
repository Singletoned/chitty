---
title: Say in the managed guide that a ticket lands only after a passing review
status: done
labels:
  - untestable
owner: untestable
created: 2026-11-22
---

## Description

Seen 2026-11-16: `TASK-318` code reached `main` before its review failed it. The runner section of the managed guide (`src/chitty/guide-runner.md`, rendered into `AGENTS.md`) tells agents started without `chitty run` to rebase, run the checks and fast-forward `main`, without saying the review must have passed first. Say that landing needs a passing review: only a reviewer whose review passed lands, never the worker. Keep the advice general (the guides reach every repository). Split from `TASK-358`, which adds the `chitty check` warning.

## Notes

Reviewed: wording checked against the ticket.

## Summary

Reworded the first paragraph of `src/chitty/guide-runner.md` (and its fixture): a ticket lands only after its review passes, a worker never lands its own ticket, and a reviewer started without `chitty run` lands only a passing review. `make check` passed (1112 tests). The `AGENTS.md` managed block picks this up when the main checkout next runs `chitty init`.

## History

- 2026-11-22T09:55:42Z friendly-jade-stoat → todo
- 2026-11-22T10:03:46Z friendly-jade-stoat: changed owner
- 2026-11-22T10:03:46Z friendly-jade-stoat todo → doing
- 2026-11-22T10:09:54Z friendly-jade-stoat: changed summary
- 2026-11-22T10:09:54Z friendly-jade-stoat doing → review
- 2026-11-22T11:31:12Z human: changed notes
- 2026-11-22T11:31:12Z human review → done
