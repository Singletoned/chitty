---
title: Quiet expected Backlog.md statuses and remove backlog/config.yml on import
status: todo
created: 2026-10-28
---

## Description

Circuitry's import printed 'unknown status Backburner' for each of 8 tasks, although Backburner is declared in backlog/config.yml. The mapping (unknown -> backlog, original kept in Notes) is right; the output is noise. Separately, backlog/config.yml is neither reported nor removed, so backlog/ survives the import without any notice. The reported non-zero exit was not reproduced on main (scratch clone of circuitry at fcca564 exits 0), so it is out of scope.

## Acceptance Criteria

- [ ] Statuses listed in backlog/config.yml 'statuses' map to backlog with one summary line per status (e.g. '8 tasks: Backburner -> backlog'); only statuses missing from that list are reported as unknown
- [ ] The Backlog.md status is still recorded in each task's Notes
- [ ] backlog/config.yml is removed under the same rules as converted task files: git rm when tracked and clean; untracked or modified files trigger the --remove-source/--keep-source choice
- [ ] Other non-task content (docs/, decisions/, etc.) stays and is reported, so backlog/ is removed only when nothing else remains
- [ ] Tests cover declared and undeclared custom statuses and config.yml removal; PLAN.md and README migration section updated

## Notes

Suggestion origin: circuitry

Decided with the human: aggregate expected-status reports from config.yml rather than adding a configurable mapping; treat config.yml as consumed by the import.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
