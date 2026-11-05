---
title: Require evidence in a review that fails a ticket
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

`src/chitty/roles/review.md` already says to fail only for "an unmet criterion or a demonstrated defect, such as a throwaway failing test". On `TASK-148` on 2026-11-05 the third review still failed the ticket on reasoning alone, claiming that an `assert` after a `finally` would hide the original error. It could not, because the `assert` is not reached while an exception propagates, and one throwaway test showed this. "Such as" reads as an example, and nothing asks the reviewer to show the evidence.

Replace two whole bullets in `src/chitty/roles/review.md`, and no others, because other tickets edit this file. Use this wording, adjusting only line wrapping.

Replace the bullet starting "Fail only" with:

"Fail only for an unmet criterion or a demonstrated defect. A claim about what code does when it runs must be run first, using an existing test, the project's check command or a throwaway test. Reasoning alone demonstrates nothing: if you can run the code but cannot show the defect, file a ticket instead of failing. File a ticket for other findings too."

Replace the bullet starting "On failure" with:

"On failure, write one note in the form `Review failed (<cause>): ...`, where the cause is `design`, `tests`, `work`, `integration`, or `review`; explain what must change and `--uncheck` every failed criterion. Set `-s doing`. The note gives what was run and what it printed. When there is nothing to run, because nothing exercises a criterion, a file is missing or the ticket itself is wrong, it says what is missing or wrong. When the environment stopped you running the code, it says what stopped you, with the cause `integration`."

This file ships to every repository, so do not name `make`.

`chitty guide review` serves this file at run time, and `AGENTS.md` does not hold it, so no `chitty init` or version bump is needed. Leave `src/chitty/guide.md` and `AGENTS.md` alone: changing them would refresh every repository's `AGENTS.md` for little gain.

`TASK-167` later extends the same failure-note bullet with a line per criterion, and it must keep this rule. If it lands first, keep its lines and add this wording to the bullet.

Out of scope: having Chitty enforce the format of a failure note, and which model reviews.

## Acceptance Criteria

- [ ] A test in `TestGuide` in `tests/test_cli.py` shows `guide("review")` containing `must be run` and `Reasoning alone demonstrates nothing`, and fails against the current `review.md`

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Serious, fixed: one criterion could pass on words already in the file, so it is now two naming exact phrases. Also fixed: failures with nothing to run, such as a missing file, a wrong ticket or a broken environment, which the rule would have forbidden; a reviewer unable to demonstrate a claim files a ticket; not naming `make`, since the file ships to every repository; the wording is given outright for a cheap worker; and `guide.md` left alone is stated. It confirmed no `chitty init` or version bump is needed. Rejected: folding this into `TASK-167`, which waits on `TASK-166` and `TASK-151`, because this is cheap to have now, so `TASK-167` is told to keep the rule instead.

## History

- 2026-11-05T17:09:01Z mellow-newt → backlog
- 2026-11-05T17:10:22Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T17:10:23Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T17:10:24Z mellow-newt backlog → todo
- 2026-11-05T18:13:35Z mellow-newt todo → backlog
- 2026-11-05T18:19:16Z mellow-newt: changed description
- 2026-11-05T18:19:17Z mellow-newt: changed acceptance criteria
