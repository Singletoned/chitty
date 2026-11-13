---
title: Require reviewers to report all findings together
status: backlog
labels:
  - workflow
  - review
priority: high
created: 2026-11-13
---

## Description

Reviewers often stop after the first defect, causing avoidable review cycles and hiding whether the whole change is coherent.

## Acceptance Criteria

- [ ] The review guide requires inspecting every acceptance criterion and the complete diff before writing the review note.
- [ ] A failing review note lists every problem found in one review, with one actionable finding per relevant criterion.
- [ ] The review guide requires checking that the changes fit together, cover useful property-test opportunities, and make sense to users.
- [ ] The guide tells a later reviewer to identify when a finding was already present in an earlier review.

## History

- 2026-11-13T19:51:41Z zesty-umber-puffin → backlog
