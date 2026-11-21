---
title: Refuse renumbering when untouched tickets link to an old ID
status: planning
depends_on:
  - TASK-391
parent: TASK-391
created: 2026-11-21
---

## Description

Extend `TASK-391`'s read-only planner before the writer in `TASK-517` can use it. Recheck the landed interface before cold reading. Reject a `parent` or `depends_on` pointing to any mapped old ID in an untouched disk file or visible authoritative ref-backed ticket. Use `ticket_ids()` and authoritative `lookup` for ref-backed results, including IDs without a disk file. Let required source-read errors propagate. Compare structured links via `TaskId.parse` and name the blocking ticket and old ID. Prose and History mentions do not block; do not inspect non-authoritative historical refs or unseen branches.

Use separate real-Git subtests in `tests/test_provisional_link_guard.py` using `RepoTestCase`. With an eligible `TASK-AAAAAA`, separately link to it from (a) an unconfigured disk file, (b) a stale main file whose authoritative ticket branch removes the link, and (c) an authoritative branch-only file. Use `depends_on` for (a) and (c), lowercase `parent` for (b), and assert the selected refs for (b) and (c). In the matching prose variants replace the structured link with a Description mention. Fixed real-Git placements verify which copies are inspected; source policy property tests are separate. Confirm the refusal assertions fail on the unguarded planner before implementing, then run the new tests and `make check`.

## Acceptance Criteria

- [ ] Each of the three fixture variants refuses a nonempty plan with an error naming both IDs, and leaves HEAD, index and bytes unchanged. Swap the structured link for a Description mention and the plan succeeds while leaving the same files outside its writable set.

## History

- 2026-11-21T18:44:38Z eager-ginger-adder → backlog
- 2026-11-21T18:45:12Z eager-ginger-adder: changed description, acceptance criteria
- 2026-11-21T18:45:12Z eager-ginger-adder backlog → planning
