---
title: Re-sample planned tickets for property tests after TASK-302
status: review
owner: human
depends_on:
  - TASK-302
created: 2026-11-12
---

## Description

- Baseline (2026-11-12): in a random sample of 15 tickets finished before TASK-302, 11 could have had a property test and one (TASK-270) did; 3 had a valid reason for none (TASK-217 docs, TASK-238 a small fixed set, TASK-246 real processes).
- Once about 15 tickets planned after TASK-302 lands are done, sample them the same way: for each, did it specify properties or give a valid one-line reason, did the worker use a generating tool, and did a review or later bug find a missed property.
- Planning-session work, not a worker ticket. Record the counts in a note and compare with the baseline; suggest guide changes if the rate has not moved.

## Notes

Re-sample, 2026-11-17: all 16 done tickets first promoted to `todo` after `TASK-302` landed (2026-11-13T11:27Z), judged from ticket text and notes. Specified properties: 4 (`TASK-320`, `TASK-321`, `TASK-330`, `TASK-325`); all 4 workers used Hypothesis, and in `TASK-320` it found two bugs. Valid one-line reason for none: 10 (`TASK-324` real process; `TASK-329`, `TASK-332`, `TASK-333`, `TASK-335` small fixed set; `TASK-336`, `TASK-360`, `TASK-361`, `TASK-362` fixed text; `TASK-337` removes code, which is not one of the guide's listed reasons but holds). Partial: `TASK-279` gave the fixed-text reason, but it also changed actor propagation. None: `TASK-314`, promoted two hours after `TASK-302` landed. So 14 or 15 of 16 followed the rule, against 4 of 15 in the baseline (1 property, 3 reasons). Missed property found later: `TASK-325` review found its generators never produced placeholders (an identity mutant passed); the review caught it. Caveat: 6 of 16 are wording tickets, which now skip the pipeline as `untestable`, so the sample leans to fixed text.

## History

- 2026-11-12T20:18:42Z kind-yellow-vole → backlog
- 2026-11-17T17:56:57Z kind-umber-toad: changed notes
- 2026-11-17T18:17:56Z kind-umber-toad backlog → review
