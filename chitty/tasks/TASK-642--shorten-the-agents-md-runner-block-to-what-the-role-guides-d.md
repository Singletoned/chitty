---
title: Shorten the `AGENTS.md` runner block to what the role guides do not say
status: cold-read
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
- Replace the omission paragraph and the return-to-planning paragraph with one sentence: a ticket that cannot guide the work goes back to `planning` with a note giving the evidence and the decision needed; external obstacles go to `blocked`; implementation defects go to `doing`.
- Tighten the landing paragraph and the review-note paragraph. Keep their rules: a worker never lands its own ticket; under `chitty run` the runner rebases, checks and fast-forwards `main`; a reviewer started by hand rebases, runs the checks, then only fast-forwards `main`; one line per criterion in the stated format; a test criterion passes only with evidence that the test fails without the change.
- Keep the list of `chitty guide` roles as it is.

Before removing a point, confirm that `work.md` or `review.md` states it, and name where in the summary. Update the snapshot `tests/fixtures/guide-runner-expected.md` to match. This repository's own `AGENTS.md` updates when the main checkout's `chitty` upgrades it after landing; do not edit it on the branch.

Rules for this tightening:
- Keep every instruction and its meaning. Remove repeats within the file, filler and roundabout phrasing. Turn a long bullet that bundles a list into a short lead line with nested bullets.
- Keep the advice general: the guides reach every repository that uses Chitty, in any language.
- Do not move rules to other files unless this ticket says to.
- In `--summary`, list each sentence removed outright and where its point still lives, so the reviewer can check nothing was lost.

## History

- 2026-11-23T12:34:57Z friendly-zinc-dormouse → planning
- 2026-11-23T12:37:49Z friendly-zinc-dormouse planning → cold-read
