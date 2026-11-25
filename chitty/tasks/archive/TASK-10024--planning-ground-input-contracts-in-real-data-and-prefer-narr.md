---
title: "Planning: ground input contracts in real data, and prefer narrowing scope over adding rules"
status: backlog
created: 2026-11-25
moved_from: TASK-XVRS67
---

## Description

Evidence (echonomicon TASK-133, "Rank live podcasts from Podcast Index rows"): a pure filter-and-sort, about 30 lines of code, grew to a ~1,100-word ticket over 9 cold reads, plus a split into TASK-BCHE6A and TASK-VY5XWK. The input was declared `Mapping[str, object]` before anyone looked at the Podcast Index dump. Every reader then asked "what if this column is null / a digit string / a bool / a float?", and each answer added a rule, an example and a test. The latest worker bounce asks the same thing about three more columns. The real dump (checked 2026-11-25 with `typeof()` over all 4,768,189 rows) has no nulls and no mixed types in any of those columns.

Cause: `chitty guide plan` says "resolve every reader finding": strengthen, split or reject. In practice findings get resolved by adding text. Nothing asks whether the case can occur. The "open inputs" property signal pushes the same way.

Suggestion for `chitty guide plan` (and the matching line in `guide cold-read`):
- Take an input contract from the real source (schema, caller, sample data) when one exists. Reject anything outside it at the boundary with one loud check. Do not specify behaviour for it.
- Before resolving a finding by adding a rule, ask whether the case occurs in practice. If it does not, resolve it by narrowing the contract or rejecting the finding, not by adding text.
- When a fix makes the ticket shorter, prefer it.

## Notes

Suggestion origin: echonomicon

Triage 2026-11-25: already built. `src/chitty/roles/plan.md` says to ground input contracts in the real source, prefer boundary validation, and prefer fixes that make the ticket shorter; `src/chitty/roles/cold-read.md` matches.

## History

- 2026-11-25T22:28:40Z calm-ochre-quail → backlog
- 2026-11-25T22:28:41Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:23Z calm-ochre-quail: changed notes
- 2026-11-25T22:33:26Z calm-ochre-quail backlog → archived
- 2026-11-25T22:35:12Z calm-ochre-quail: renumbered from TASK-XVRS67
