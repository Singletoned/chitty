---
title: Require evidence in a review that fails a ticket
status: doing
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

`src/chitty/roles/review.md` already says to fail only for "an unmet criterion or a demonstrated defect, such as a throwaway failing test". On `TASK-148` on 2026-11-05 the third review still failed the ticket on reasoning alone, claiming that an `assert` after a `finally` would hide the original error. It could not, because the `assert` is not reached while an exception propagates, and one throwaway test showed this. "Such as" reads as an example, and nothing asks the reviewer to show the evidence.

Replace two whole bullets in `src/chitty/roles/review.md`, and no others, because other tickets edit this file. Use this wording, adjusting only line wrapping.

Replace the bullet starting "Fail only" with:

"Fail only for an unmet criterion or a demonstrated defect. A criterion is unmet if nothing exercises it, if a file it needs is missing, or if the environment stopped you verifying it. A ticket that is itself wrong also fails, with the cause `design`. A claim about what code does when it runs must be run first, using an existing test, the project's check command or a throwaway test. Reasoning alone demonstrates nothing: if you can run the code but cannot show the defect, file a ticket instead of failing. File a ticket for other findings too."

Replace the bullet starting "On failure" with:

"On failure, write one note in the form `Review failed (<cause>): ...`, where the cause is the earliest stage that should have caught it: `design`, `tests`, `work`, `integration` (branch, merge, environment), or `review`. Explain what must change and `--uncheck` every failed criterion. Set `-s doing`. If you ran code, the note gives what was run and what it printed. If there was nothing to run, it says what is missing or wrong. If the environment stopped you running the code, it says what stopped you, with the cause `integration`."

This file ships to every repository, so do not name `make`.

`chitty guide review` serves this file at run time, and `AGENTS.md` does not hold it, so no `chitty init` or version bump is needed. Leave `src/chitty/guide.md` and `AGENTS.md` alone: changing them would refresh every repository's `AGENTS.md` for little gain.

`TASK-167` later extends the same failure-note bullet with a line per criterion, and it must keep this rule. If it lands first, keep its lines and add this wording to the bullet.

Out of scope: having Chitty enforce the format of a failure note, and which model reviews.

## Acceptance Criteria

- [ ] A test in `tests/test_guide_review_evidence.py`, collapsing whitespace in `guide("review")` first so that line wrapping cannot break it, shows it containing `A criterion is unmet if nothing exercises it`, `A ticket that is itself wrong also fails`, `must be run first`, `Reasoning alone demonstrates nothing`, `file a ticket instead of failing`, `earliest stage that should have caught it`, `If you ran code, the note gives what was run and what it printed`, `says what is missing or wrong` and `what stopped you`, and fails against the current `review.md`
- [x] The same test shows `guide("review")` still containing `Review failed (<cause>):`, `--uncheck` and `-s doing`, no longer containing `such as a throwaway failing test`, and not matching `\bmake\b`

## Plan

Update the review role's two specified bullets exactly as ticketed, add the TestGuide regression assertions with collapsed whitespace, run the focused test and full make check, then apply chitty fix and record verification.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-05. Serious, fixed: one criterion could pass on words already in the file, so it is now two naming exact phrases. Also fixed: failures with nothing to run, such as a missing file, a wrong ticket or a broken environment, which the rule would have forbidden; a reviewer unable to demonstrate a claim files a ticket; not naming `make`, since the file ships to every repository; the wording is given outright for a cheap worker; and `guide.md` left alone is stated. It confirmed no `chitty init` or version bump is needed. Rejected: folding this into `TASK-167`, which waits on `TASK-166` and `TASK-151`, because this is cheap to have now, so `TASK-167` is told to keep the rule instead.

Implementing cold read by a fresh Haiku subagent, 2026-11-05, the first read of this kind here, kept at `refs/cold-read/TASK-193/1`. Serious, fixed: the wording I gave could be read as dropping the note's required form, its causes and `--uncheck`, so both bullets are now given whole; and "file a ticket" contradicted failing on a broken environment or a missing file, so it now applies only when the code runs and the defect cannot be shown. Also fixed: tests collapse whitespace; ticket advice is no longer said twice; and the `make` check covers the whole file, which has no other use of it. Rejected: testing more than phrases, because the bullets are given word for word and the reviewer can compare them. Another read follows.

Second implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-193/2`. Serious, fixed: my rewrite still contradicted itself, because "fail only" excluded the cases the failure note then asked for, namely a criterion nothing exercises, a missing file, a wrong ticket and a broken environment, so the first bullet now names them. Also fixed: "what was run" now applies only when code ran; the causes had no meaning in this file, so it now uses `PLAN.md`'s definition; and the test checks the old wording is gone. A third read follows.

Third implementing cold read by a fresh Haiku subagent, 2026-11-05, kept at `refs/cold-read/TASK-193/3`: nothing serious. The test failed on all ten checks without the change and passed with it, and `make check` exited 0. Fixed: a wrong ticket now names its cause, one clause that the criteria's phrases still match, so no further read. Rejected: defining every cause in the file, because "earliest stage" with the list is enough and the file should stay short; a defect outside the criteria, which the bullet already allows to fail when demonstrated; an unmet criterion against an unshown defect, since the first is about a criterion and the second about a claim; and `src/chitty/guide.md` staying as it is, which is deliberate and does not contradict this.

Review failed (integration): rebasing onto `main` conflicts in `tests/test_cli.py`.

Review failed (integration): rebasing onto `main` conflicts in `tests/test_cli.py`.

Review failed (integration): rebasing onto `main` conflicts in `src/chitty/roles/review.md`, `tests/test_cli.py`.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Unblocked by a human-run session. All three failed reviews were rebase conflicts with `main`, mostly on `tests/test_cli.py`'s guide tests and `__version__`, not problems with the work. Rebased onto `main` (`0.1.40`):
- Both sides of each conflicting guide test are kept.
- The new `main` guide text sits alongside this ticket's change; the role files keep `TASK-219`'s sentence.
- `chitty.toml` and `AGENTS.md` match `main` (`TASK-212`, `TASK-218`).
- `__version__` is `0.1.41`.
`make check` passes (360 tests). Several open tickets also use `0.1.41`, so whichever lands second will need its version bumped again.

Review failed (work): check exited with status 2:
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run python scripts/check_version_bump.py
check_version_bump: changed files require a version above main (0.1.41), but working tree has 0.1.41:
  src/chitty/roles/review.md
make: *** [check] Error 1

Owner set to `human` on 2026-11-07, before `chitty run --mode work` looped on it as it did 54 times on `TASK-179`: the branch has `__version__` 0.1.41 and `main` has 0.1.42, so the check fails, and in work mode a failed check only adds a note and leaves the ticket in `doing`, so no agent starts to fix it. `TASK-224` removes branch version bumps. Clear the owner once it lands.

Unparked: TASK-227 now lets a worker fix a failing check on a doing ticket. Recheck this branch before review.

Aligned the guide regression-test location with current repository guidance: use a dedicated `tests/test_guide_<topic>.py` file rather than adding to `TestGuide` in `tests/test_cli.py`.

## Summary

Updated the two review-role bullets and added TestGuide regression assertions requiring executable evidence and structured failure notes. Verified the focused regression test, make check (ruff, pyright, 278 unittest tests, and npm test), and chitty fix; fix reported only pre-existing task-format warnings.

## History

- 2026-11-05T17:09:01Z mellow-newt → backlog
- 2026-11-05T17:10:22Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T17:10:23Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T17:10:24Z mellow-newt backlog → todo
- 2026-11-05T18:13:35Z mellow-newt todo → backlog
- 2026-11-05T18:19:16Z mellow-newt: changed description
- 2026-11-05T18:19:17Z mellow-newt: changed acceptance criteria
- 2026-11-05T18:19:18Z mellow-newt: changed acceptance criteria
- 2026-11-05T18:19:19Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T18:19:59Z mellow-newt: changed acceptance criteria
- 2026-11-05T18:20:00Z mellow-newt: changed acceptance criteria
- 2026-11-05T18:31:03Z mellow-newt: changed description, acceptance criteria
- 2026-11-05T18:31:04Z mellow-newt: changed acceptance criteria
- 2026-11-05T18:31:05Z mellow-newt: changed acceptance criteria, notes
- 2026-11-05T18:35:43Z mellow-newt: changed description, notes
- 2026-11-05T18:35:43Z mellow-newt backlog → todo
- 2026-11-05T23:52:34Z youthful-adder todo → doing
- 2026-11-06T00:00:20Z youthful-adder: wrote the plan
- 2026-11-06T00:06:42Z youthful-adder: ticked acceptance criteria
- 2026-11-06T00:06:43Z youthful-adder: ticked acceptance criteria
- 2026-11-06T00:06:44Z youthful-adder: changed summary
- 2026-11-06T00:06:45Z youthful-adder doing → review
- 2026-11-06T14:43:33Z lively-quail: changed notes
- 2026-11-06T14:43:33Z lively-quail review → doing
- 2026-11-06T16:32:01Z youthful-vole: changed summary
- 2026-11-06T16:32:10Z youthful-vole doing → review
- 2026-11-06T16:56:05Z jolly-gannet: changed notes
- 2026-11-06T16:56:05Z jolly-gannet review → doing
- 2026-11-06T18:36:27Z vivid-dormouse: changed summary
- 2026-11-06T18:36:27Z vivid-dormouse doing → review
- 2026-11-06T18:37:36Z brisk-quail: changed owner, notes
- 2026-11-06T18:37:36Z brisk-quail review → blocked
- 2026-11-06T21:41:01Z youthful-toad: changed owner, notes
- 2026-11-06T21:41:01Z youthful-toad blocked → review
- 2026-11-06T21:55:13Z kind-raven: changed notes
- 2026-11-06T21:55:13Z kind-raven review → doing
- 2026-11-07T09:39:55Z vivid-dormouse: changed owner, notes
- 2026-11-08T13:05:02Z eager-puffin: changed owner, notes
- 2026-11-08T13:08:50Z eager-puffin: changed acceptance criteria, notes
