---
title: Reviewers should report every problem in one review
status: backlog
created: 2026-11-19
---

## Description

Reviewers currently tend to stop at the first failing problem, so a ticket goes round once per defect and escalates after three rounds even when every defect was findable in the first review. Evidence from echonomicon on 2026-11-13: TASK-141, TASK-143 and TASK-150 each failed review three times, and each review found one new problem the previous review could have found (TASK-141: the formatter test, then the fixture location, then missing artifacts being skipped; TASK-150: the run fixture, then a test isolation gap, then an assertion outside the isolated filesystem). Proposal: `chitty guide review` should tell the reviewer to check every criterion and the whole diff before writing the note, list every problem found, and only then fail the ticket; a later review that finds a problem that was already present in an earlier one should say so, so planners can see the review missed it.

## Notes

Suggestion origin: echonomicon

Archived: `src/chitty/roles/review.md` already says to inspect every criterion and the whole diff, not stop at the first defect, report all findings in one note, and cite earlier notes for unresolved findings.

## History

- 2026-11-19T20:55:08Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:09Z sunny-white-dormouse: changed notes
- 2026-11-19T20:58:43Z sunny-white-dormouse: changed notes
- 2026-11-19T20:58:46Z sunny-white-dormouse backlog → archived
