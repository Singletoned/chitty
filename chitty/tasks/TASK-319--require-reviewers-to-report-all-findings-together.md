---
title: Require reviewers to report all findings together
status: review
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

- [x] The review guide requires inspecting every acceptance criterion and the complete diff before writing the review note.
- [x] A failing review note reports all findings from that pass together, with actionable findings grouped by criterion; a criterion may have multiple findings.
- [x] The review guide requires checking that the changes fit together, cover useful property-test opportunities, and make sense to users.
- [x] The guide distinguishes newly discovered findings from previously reported findings that remain unresolved. Discovering another bug on a later pass is expected, not evidence of an earlier process failure.

## Plan

Update the review guide and pipeline design notes to require a complete inspection before one consolidated verdict, preserving dirty-worktree and verification-limit handling. Group all actionable findings under the existing criterion lines, and distinguish new discoveries from unresolved earlier findings without blaming prior reviewers. Add fixed-text rendered-guide regression tests (no property tests: fixed instructions with no variable input), demonstrate failure before the guidance change, then run format and all checks. Scope excludes runner changes and review-note parsing.

## Summary

Implemented in commit 14670e2. Updated `src/chitty/roles/review.md` and `docs/plan/pipeline-and-feedback.md`: inspect the complete change before a consolidated verdict, report all findings per pass, preserve dirty-worktree and verification-limit handling, and distinguish new discoveries from unresolved earlier findings without treating later discoveries as earlier process failures. Added `tests/test_guide_review_completeness.py`: all three tests failed before the guidance change (15 failing subtests), then passed with the change. `make format` and `make check` pass, including existing review-evidence tests. Fixed-text guidance needs no property tests. Ready for independent review; not merged.

## History

- 2026-11-13T19:51:41Z zesty-umber-puffin → backlog
- 2026-11-13T22:24:02Z brisk-yellow-urchin: changed acceptance criteria; wrote the plan
- 2026-11-13T22:24:02Z brisk-yellow-urchin backlog → doing
- 2026-11-13T22:25:44Z brisk-yellow-urchin: changed summary; ticked acceptance criteria
- 2026-11-13T22:25:44Z brisk-yellow-urchin doing → review
