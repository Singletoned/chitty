---
title: "Baseline: classify every past review failure by cause"
status: todo
priority: high
owner: human
parent: TASK-106
created: 2026-11-03
---

## Description

Hand-run the first retro, so the spec-first pilot has something to be compared with. History shows 23 failed reviews across 14 of 50 reviewed tickets; a quick first pass over the 22 notes it could find gave 14 missed cases, 5 weak tests, 2 branch or merge problems and 1 unmet docs criterion. That pass was rough and read truncated notes, and it did not separate cases the ticket stated from cases it left out, which is the distinction that matters.

Read-only over tickets and Git, apart from this ticket and any tickets it proposes. Do not change rules or prompts here: proposals go to the human.

This is for the planning session, not a worker: it needs judgement about why reviews failed, and it proposes rules for the human. Owner `human` is how `chitty next` and `chitty run` skip it.

Recount rather than trusting the figures above, which were rough and are now out of date: a raw count on 2026-11-04 found `review → doing` 36 times across 21 task files. Count failures from each task's `## History`, including archived tickets, and use notes for the reason. Several failure notes do not say `Review failed`. Include failures up to the day this runs, and say the date. Map the first pass's categories to `PLAN.md`'s causes: criterion 2 is what splits a missed case between `design` and `work`. First-pass yield is reviewed tickets that passed their first review, divided by all reviewed tickets. The report goes in this ticket's notes, and the two candidate proposals below count towards the three.

## Acceptance Criteria

- [ ] Every failed review in History is listed with its ticket and one cause from `PLAN.md`, or `unknown` with the reason; the count reconciles with History
- [ ] Each failure records whether it cited a stated criterion or a case the ticket left out
- [ ] Reports first-pass yield, retries per ticket and failures by cause, and states what it could not measure, including post-`done` escapes
- [ ] Proposes at most three changes to standing rules, each naming the failure class it should reduce, for the human to accept or reject

## Notes

Candidate proposal for the retro: a scripted check that fails when `src/chitty/guide.md` changes without a `__version__` bump. `TASK-104` lost its bump in a rebase with its criterion still ticked, and a reviewer had to spot it.

Second candidate for the retro: a scripted check that `__version__` is above `main`'s when the guide or extension changes. Two tickets bumping to the same version merge silently, and repositories then never learn about the later change.

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: which history to count, stale figures, the mapping to causes, a formula for yield, and where the report goes.

## History

- 2026-11-03T10:27:46Z lively-panda → backlog
- 2026-11-03T10:28:25Z lively-panda: changed acceptance criteria
- 2026-11-03T10:41:02Z lively-panda: changed notes
- 2026-11-03T20:44:58Z lively-panda: changed notes
- 2026-11-04T19:32:41Z mellow-newt: changed owner, description
- 2026-11-04T19:36:35Z mellow-newt: changed description, notes
- 2026-11-04T19:36:36Z mellow-newt backlog → todo
