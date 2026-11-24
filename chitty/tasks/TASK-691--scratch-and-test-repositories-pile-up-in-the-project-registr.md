---
title: Scratch and test repositories pile up in the project registry
status: backlog
created: 2026-11-24
---

## Description

On 2026-11-23 the inbox registry (`inbox_path('_').parent`) held 41 projects, of which only about 10 are real repositories. The rest are left by agent probes and possibly tests: `tmp-a3nxft7jox`, `tmp-mh4uvb1knb`, `tmp-vxeisezmeh` (paths under `/private/var/folders/.../T/tmp.*`), `tmps0tf3zag` (registered to `.worktrees/task-401/tmps0tf3zag` in this repo, which suggests a test that ran without `RepoTestCase`'s temporary `XDG_DATA_HOME`), `probe*`, `rep`, `rep2`, `r568`, `t559repo`, `t559show`, `ac`, `ac-probe`, `p520`, `tk` and `duetry` (session scratchpads). Many paths no longer exist. They clutter `chitty suggest` completion and the "known projects" error. Suggest: find which test registers `tmps0tf3zag` and give it a temporary data home; and have `chitty suggest` (or a cleanup step) warn about registered projects whose repository path is gone, rather than deleting them silently.

## Notes

Suggestion origin: chitty

## History

- 2026-11-24T22:21:53Z zesty-coral-newt → backlog
- 2026-11-24T22:21:54Z zesty-coral-newt: changed notes
