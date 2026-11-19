---
title: Require criterion-to-test evidence in implementing cold reads
status: backlog
created: 2026-11-19
---

## Description

In injustice-league planning, two implementing cold readers reported READY despite missing explicitly required generated full-record/per-field mutation tests. Superseded commit deea459:tests/test_incidents.py had five tests, only one generated kind/delta enum and fixed records; parent source inspection exposed the gap. A fresh read with explicit strategy requirements produced d262283 and proper report/incident generators, mutations, recursive JSON and URL category coverage. Update the cold-read guide to require a concise acceptance-clause-to-test-function matrix with generated inputs/state, baseline failures and exact fixed mutant edits/results. Unexercised clauses must prevent READY even when make check passes. Expected benefit: fewer false-ready tickets and repeated planning reads; cost: a short structured evidence section. The Pi workflow proposal is also recorded in ~/.pi/IMPROVEMENTS.md.

## Notes

Suggestion origin: injustice-league

Archived: Chitty cold readers do not implement the ticket, so a criterion-to-test matrix of an implementation does not apply; the weak-tests report in `src/chitty/roles/cold-read.md` covers the Chitty case.

## History

- 2026-11-19T20:55:30Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:32Z sunny-white-dormouse: changed notes
- 2026-11-19T20:58:56Z sunny-white-dormouse: changed notes
