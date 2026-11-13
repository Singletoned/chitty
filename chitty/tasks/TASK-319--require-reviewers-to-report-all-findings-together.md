---
title: Require reviewers to report all findings together
status: doing
labels:
  - workflow
  - review
priority: high
created: 2026-11-13
moved_from: BACKLOG-93769170
---

## Description

Reviewers often stop after the first defect, causing avoidable review cycles and hiding whether the whole change is coherent.

## Acceptance Criteria

- [ ] The review guide requires inspecting every acceptance criterion and the complete diff before writing the review note.
- [ ] A failing review note reports all findings from that pass together, with actionable findings grouped by criterion; a criterion may have multiple findings.
- [ ] The review guide requires checking that the changes fit together, cover useful property-test opportunities, and make sense to users.
- [ ] The guide distinguishes newly discovered findings from previously reported findings that remain unresolved. Discovering another bug on a later pass is expected, not evidence of an earlier process failure.

## Plan

Update the review guide and pipeline design notes to require a complete inspection before one consolidated verdict, preserving dirty-worktree and verification-limit handling. Group all actionable findings under the existing criterion lines, and distinguish new discoveries from unresolved earlier findings without blaming prior reviewers. Add fixed-text rendered-guide regression tests (no property tests: fixed instructions with no variable input), demonstrate failure before the guidance change, then run format and all checks. Scope excludes runner changes and review-note parsing.

## History

- 2026-11-13T19:51:41Z zesty-umber-puffin → backlog
- 2026-11-13T22:24:02Z brisk-yellow-urchin: changed acceptance criteria; wrote the plan
- 2026-11-13T22:24:02Z brisk-yellow-urchin backlog → doing
