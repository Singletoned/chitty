---
title: Review parent tickets as complete change collections
status: backlog
labels:
  - workflow
  - parent
priority: high
created: 2026-11-13
---

## Description

Parent tickets group related child work and may have no code commits of their own. Reviewers need to evaluate the completed collection, not treat the last child as the parent review.

## Acceptance Criteria

- [ ] Planning, work, and review guides explain that a parent moves to review after its children are complete.
- [ ] Parent review verifies every child is done and checks the parent criteria against the complete collection of changes.
- [ ] Parent review explicitly considers whether the changes fit together, whether property tests are appropriate, and whether the result makes sense to users.
- [ ] chitty run can review a parent with no branch without blocking solely because the branch is absent.
- [ ] A passing branchless parent review completes the parent without requiring a merge of an empty branch.

## History

- 2026-11-13T19:51:40Z zesty-umber-puffin → backlog
