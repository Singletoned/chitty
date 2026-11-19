---
title: Fix two flaky Hypothesis tests that send runner tickets to `error`
status: backlog
created: 2026-11-19
---

## Description

On `main` (2026-11-19) two property tests fail at random under `make check` and have sent `TASK-388` and `TASK-395` to `error` (runner check failures). (1) `tests/test_property_refused_write.py` `test_refused_edit_restores_repository`: the `NOTES` strategy can draw a setext underline, for example note `0\n=`, which `model.parse` rejects with `Notes text changed section boundaries`, not the asserted `cannot finalize task write`. Reproduced on `main` by calling the inner test with `("self-dependency", "0\n=", None)`. Fix: filter lines made only of `=` or `-` (up to three leading spaces) from `NOTES`. (2) `tests/test_property_provisional.py` `test_suffix_round_trips` exceeded the default 200 ms Hypothesis deadline (278 ms) under 16 parallel workers; `TASK-406` and `TASK-382` reviews saw the same. Fix: register and load a Hypothesis profile with `deadline=None` in `tests/__init__.py`, so no test depends on machine load.

## Notes

Suggestion origin: chitty

Archived as covered by `TASK-417` (done).

## History

- 2026-11-19T20:55:20Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:22Z sunny-white-dormouse: changed notes
- 2026-11-19T20:56:41Z sunny-white-dormouse: changed notes
