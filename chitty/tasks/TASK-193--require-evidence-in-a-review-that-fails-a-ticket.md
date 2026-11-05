---
title: Require evidence in a review that fails a ticket
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

`src/chitty/roles/review.md` already says to fail only for "an unmet criterion or a demonstrated defect, such as a throwaway failing test". On `TASK-148` on 2026-11-05 the third review still failed the ticket on reasoning alone, claiming that an `assert` after a `finally` would hide the original error. It could not, because the `assert` is not reached while an exception propagates. One throwaway test showed this, but that failure had already blocked the ticket for a person. "Such as" reads as an example, and nothing asks the reviewer to show the evidence.

In `src/chitty/roles/review.md`, make that bullet say that a claim about what code does must be run before it can fail a ticket, and that reasoning alone demonstrates nothing. Make the bullet on failure notes require the note to give what was run and what it printed. A criterion unmet because nothing exercises it needs no run: the note names what is missing. A failing `make check` counts as a run.

Keep the file short, and touch only these bullets, because other tickets edit this file. `chitty guide review` serves this file, and `AGENTS.md` does not hold it, so no `chitty init` or version bump is expected: check that.

Out of scope: having Chitty enforce the format of a failure note, and which model reviews.

## Acceptance Criteria

- [ ] A test in `TestGuide` in `tests/test_cli.py` shows `guide("review")` requiring a claim about code to be run, and a failure note to give what was run and what it printed

## History

- 2026-11-05T17:09:01Z mellow-newt → backlog
