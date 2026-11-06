---
title: Find what leaves temporary projects in the real inbox
status: doing
labels:
  - bug
priority: low
parent: TASK-106
created: 2026-11-04
---

## Description

`~/.local/share/chitty/inbox` holds `chitty-run-txsmwm`, `chitty-task-123-tlk9qr`, `prj`, `repo`, `t45`, and several `tmp-*` directories, seen on 2026-11-04. They look like temporary repositories, so something registered them outside a test's temporary `XDG_DATA_HOME`. It may be a test that does not inherit `RepoTestCase`, or an agent's hand trial of `chitty init` in a scratch repository. `chitty init` registers a project without asking. They do no harm beyond appearing as known projects in `chitty suggest`'s errors.

The cold read found most of the cause from each directory's `repo` owner file: `tmp-*`, `t45`, `chitty-task-123-tlk9qr` and `chitty-run-txsmwm` point at scratch directories, so they were hand trials of `chitty init`. `repo` matches the layout of `RepoTestCase`, and `prj` has an empty owner file, so those two may be tests, both from about 1 November. Compare a listing of the real inbox before and after a full test run. Fix any test that changes it, and record the result. Removing the directories is for the human, so list them in the note.

## Acceptance Criteria

- [x] A note records the before and after listing of the real inbox around a full test run, and what caused each directory

## Plan

1. Record the real inbox listing before a full test run.
2. Run the repository's complete check suite and record the after listing.
3. Inspect test setup and any changed files to identify whether the suite caused entries; fix a test only if the run demonstrates a regression.
4. Record the evidence and causes in the ticket note, run chitty fix, and summarize the verified result.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. It found the likely cause, and the check now names how to show it.

Full-suite inbox comparison (2026-11-06): before and after make check were identical. Both contained: chitty, chitty-run-txsmwm, chitty-task-123-tlk9qr, chladnify, circuitry, context-mode, echonomicon, prj, repo, spend-model, t45, taidy, task149-scratch, tmp-1soka7lhma, tmp-mehm3w3igo, tmp-mn1utr3ave, tmp-xv9qiiwofj, tmp-yhztcyxx4f, and tmpoc0f637i. make check passed: Ruff, Pyright, 277 Python unittest tests, and Node tests. RepoTestCase sets an isolated temporary XDG_DATA_HOME, so the suite did not write the real inbox; no test fix was needed.

Cause review from each repo owner file: chitty, chladnify, circuitry, echonomicon, spend-model, and taidy are real registered projects. chitty-run-txsmwm, chitty-task-123-tlk9qr, t45, task149-scratch, and all six tmp-* / tmpoc0f637i entries point into /tmp or temporary scratch paths, identifying hand trials of chitty init. repo points to a temporary ctx-mode scratch repo and is also a hand trial. prj has an empty owner file, so it was registered without a checkout path; its origin cannot be established from inbox data. context-mode has an empty-owner repo file plus suggestions, so it is a real registered project whose owner path was not recorded. The temporary entries listed for human removal are: chitty-run-txsmwm, chitty-task-123-tlk9qr, prj, repo, t45, task149-scratch, tmp-1soka7lhma, tmp-mehm3w3igo, tmp-mn1utr3ave, tmp-xv9qiiwofj, tmp-yhztcyxx4f, and tmpoc0f637i.

## Summary

Verified handoff: the real inbox listing was unchanged by a complete make check run. RepoTestCase isolates XDG_DATA_HOME, so no test caused the entries and no code change was required. The note records the before/after names, suite results, owner-file evidence, likely causes, and the temporary directories for human removal.

## History

- 2026-11-04T21:00:17Z mellow-newt → backlog
- 2026-11-04T21:01:56Z mellow-newt: changed description, acceptance criteria, notes
- 2026-11-04T21:01:57Z mellow-newt backlog → todo
- 2026-11-06T00:28:18Z youthful-crane todo → doing
- 2026-11-06T00:28:30Z youthful-crane: wrote the plan
- 2026-11-06T00:32:15Z youthful-crane: changed notes
- 2026-11-06T00:32:21Z youthful-crane: ticked acceptance criteria
- 2026-11-06T00:32:22Z youthful-crane: changed summary
