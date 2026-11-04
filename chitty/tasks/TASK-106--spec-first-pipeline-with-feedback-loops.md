---
title: Spec-first pipeline with feedback loops
status: backlog
priority: high
created: 2026-11-02
---

## Description

Change how work moves through Chitty so a strong model and the human design each ticket, cheap models do the mechanical stages, and the system learns from its own failures. The design is `PLAN.md`, "Pipeline and feedback". This ticket is the parent: it owns the design, and its children do the work.

Pilot before building (decided with the human, 2026-11-03). `TASK-108` sets a baseline, `TASK-109` runs the pipeline by hand on 3 to 5 tickets, and `TASK-110` then builds only what the pilot justifies.

### Why it changed

The first version of this ticket specified the stages but not what makes a good ticket or how the system improves. Two conversations and the review history moved the emphasis:

- A ticket is good if a fresh agent can do it and know when to stop, and a second fresh agent can check the result without talking to the first. Writing tickets, not running workers, is the bottleneck.
- Tests are independent evidence only if derived from the spec rather than from the code. `TASK-46` failed review three times because the worker's regression test did not catch the bug.
- Agents do not learn from correction. A lesson counts only once it lands in a check, a template or a file read at session start.
- Trust does not build up in agents, so scripted gates never relax. Only the human's sampling rate changes, based on measured escapes.

### Decisions kept from the first version

Statuses and text identifiers use hyphens. A stage is one status, with claiming recorded separately. Nobody reviews a stage they did, and the test writer does not do the work. Work and review-work block for a human if the design or tests are wrong, and never edit the spec tests. A ticket can skip stages with a recorded reason.

### Decisions changed

- `review-tests` becomes `review-ticket`, done by the human for now: is the ticket small and well specified, and do the tests match it or are they hallucinated? It is the human sign-off, replacing the one at the end of `design`.
- At most one ticket in `work` at a time, merged before the next starts.
- Retry in a fresh session every time; a failure becomes a new criterion. Stop for the human after the second failure.
- Generic configurable stages and per-stage agent modes wait for the pilot's evidence (`TASK-110`).

Starting frequencies, expected to change: a retro every 10 `done` tickets and an audit of 1 in 5. The human's time is the limit on both.

## Acceptance Criteria

- [ ] `TASK-108` has reported a baseline
- [ ] `TASK-109` has reported, with a keep, change or drop decision for every stage
- [ ] `PLAN.md` and `TASK-110` reflect those decisions

## Notes

Left `chats/` uncommitted, on the assumption the transcripts are private: the points that matter are summarised here and in `PLAN.md`. Cheap to change.

Retro: `make check` before every commit is only a prompt rule, and I broke it by accident. On 2026-11-03 I chained `make check` and `git commit` without `&&`, so `PLAN.md` was committed while the check was failing, because this checkout had no dev dependencies installed. It cost one extra diagnosis round and nothing broke, as the change was docs only. Nothing mechanical would have stopped it had the change been code.

Retro: `AGENTS.md` reaches every worker, so planning instructions there leak. A `TASK-132` worker tried a cold read twice, recorded it as required, and promised to retry before review. Moved the procedure to `PLAN.md` on 2026-11-04. Question for the retro: what else in `AGENTS.md` is for one seat only? Also unexplained: its `explorer` subagent failed both times with `Agent is already processing. Specify streamingBehavior`.

## History

- 2026-11-02T17:11:36Z lively-otter → backlog
- 2026-11-03T10:28:24Z lively-panda: changed title, description, acceptance criteria, notes
- 2026-11-03T12:39:05Z lively-panda: changed notes
- 2026-11-04T09:15:49Z lively-panda: changed notes
