---
title: Shorten the `AGENTS.md` runner block to what the role guides do not say
status: doing
labels:
  - untestable
owner: untestable
depends_on:
  - TASK-640
  - TASK-608
created: 2026-11-23
---

## Description

`src/chitty/guide-runner.md` is the second half of the block `chitty init` writes into every repository's `AGENTS.md`, so every agent reads it in every session. It repeats two long paragraphs that the role guides already contain:
- the "small omission" default (`Decided: ...`), also in `src/chitty/roles/work.md` and `src/chitty/roles/review.md`;
- the list of reasons to return a ticket to `planning`, and what the note must contain, also in both role guides.

`docs/plan/agent-instructions.md` describes the block as "a short pointer: Markdown and shell quoting rules, landing, review-note format, and which `chitty guide <role>` to run".

Change `src/chitty/guide-runner.md`:
- Replace the omission paragraph and the return-to-planning paragraph with this sentence: "A ticket that cannot guide the work goes back to `planning` with a note giving the evidence and the decision needed; external obstacles go to `blocked`, implementation defects to `doing`."
- Tighten the landing paragraph and the review-note paragraph. Keep their rules: a worker never lands its own ticket; under `chitty run` the runner rebases, checks and fast-forwards `main`; a reviewer started by hand rebases, runs the checks, then only fast-forwards `main`; one line per criterion in the stated format; a test criterion passes only with evidence that the test fails without the change.
- Keep the list of `chitty guide` roles as it is.

"A worker never lands its own ticket" is in no role guide, so it stays here. `TestSplitGuide` in `tests/test_guide_workflow_block.py` (no sentence of the first block repeated in this file) must still pass. Before removing a point, confirm that `work.md` or `review.md` states it, and name where in the summary. Update the snapshot `tests/fixtures/guide-runner-expected.md` to the full output of `managed_guide("runner")`: the tickets block first, then the new runner text. This repository's own `AGENTS.md` updates when the main checkout's `chitty` upgrades it after landing; do not edit it on the branch.

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In the ticket's Summary (`chitty edit --summary-file`), list each sentence removed outright and where its point still lives. That list is how the reviewer checks nothing was lost: these tickets have no acceptance criteria, and after `TASK-640` no test checks guide wording. Length is judged, not measured.

## Summary

Done on branch `task-642` (commit `846d04d3`, on top of `task-655`, because both change `src/chitty/guide-runner.md`). `make check` passes, including `TestSplitGuide`; `tests/fixtures/guide-runner-expected.md` regenerated from `managed_guide("runner")`.

Removed outright, and where each point still lives:
- "Workers may resolve a small omission ... cheap-to-reverse default" and "It must preserve requirements ... setting": `work.md` "Omission exception" bullet; `review.md` "Check the `Decided:` note" bullet.
- "Record `Decided: <case> -> <choice>, because <reason>`, cite the precedent, and add a focused test where testable": `work.md` "Omission exception", second sub-bullet.
- "Reviewers check the choice, precedent, and test against the same boundary": `review.md` "Check the `Decided:` note" bullet.
- "Do not invent or weaken a test needed to verify a stated criterion": `work.md` omission sub-bullet and `review.md` `Decided:` bullet.
- The return-to-planning list of reasons: `work.md` "Set `-s planning`" bullet; `review.md` "Apart from that exception, set `-s planning`" bullet.
- "Stop implementation, not investigation, at the first planning blocker": `work.md` "At the first such problem" bullet.
- "Before changing status, finish reading the ticket and checking relevant code and tests": `work.md` same bullet; `review.md` "Before returning a ticket to `planning`" bullet.
- "Report all actionable planning issues in one note with evidence and the decision or correction needed" and "Say what could not be checked and why, and continue with independent checks": the same two bullets; the new summary sentence also says the note gives evidence and the decision needed.
- "Preserve existing implementation work and follow normal planning and cold-read readiness before resuming": `work.md` "Keep the branch and worktree" and "Resume there after planning and cold-read readiness"; `review.md` "Keep the branch and worktree ... resume there after planning and cold-read readiness".
- "Implementation defects ... `doing`; external obstacles ... `blocked`": kept in the new summary sentence; also `review.md` ("Set `-s doing` for implementation defects", "Use `blocked` instead") and `work.md` ("set `-s blocked`").

Tightened, nothing removed: the landing paragraph (worker never lands its own ticket; runner rebases, runs setup and checks, then fast-forwards; reviewers under the runner do not merge or remove branches or worktrees; a hand-started reviewer rebases, checks, then only fast-forwards) and the review-note paragraph (first line, one line per criterion in the stated format, evidence, and the fail-without-the-change rule with `TASK-655`'s regression-test exception). Role list unchanged.

## History

- 2026-11-23T12:34:57Z friendly-zinc-dormouse → planning
- 2026-11-23T12:37:49Z friendly-zinc-dormouse planning → cold-read
- 2026-11-23T12:40:57Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:28Z friendly-zinc-dormouse: changed description
- 2026-11-23T12:44:28Z friendly-zinc-dormouse cold-read → planning
- 2026-11-23T12:45:01Z friendly-zinc-dormouse planning → todo
- 2026-11-24T22:56:05Z mellow-teal-jay: changed summary
- 2026-11-24T23:17:35Z human todo → doing
