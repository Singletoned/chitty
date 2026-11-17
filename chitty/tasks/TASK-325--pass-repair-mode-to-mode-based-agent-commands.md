---
title: Pass repair mode to mode-based agent commands
status: done
parent: TASK-318
created: 2026-11-13
---

## Description

`chitty run --errors` repairs a ticket in `error`, but `_agent_command` in `src/chitty/run.py` renders `{mode}` from `action.mode`, which is `work` for a repair. A `{prompt}` command gets the repair guide through a special case (`status == "error"` → `guide("repair", ticket)`), but a `{mode} {id}` command receives `work` and may start an ordinary worker.

Take the substitution out of `_agent_command` into a pure function in `src/chitty/run.py`:

`render_command(words: Sequence[str], mode: str, ticket_id: str, prompt: str) -> tuple[str, ...]`

which, per word and in today's order, expands a leading `~` (`os.path.expanduser` on the raw word), then replaces `{mode}`, then `{id}`, then `{prompt}`. Replacing `{prompt}` last keeps placeholder text inside the prompt literal. `_agent_command` computes the mode as `repair` when the ticket status is `error` and `action.mode` otherwise, and passes it to `render_command`. `NextAction.mode` stays `work | review`. The `{prompt}` path keeps giving the repair guide for an error ticket. Continuation prompts, `--errors` selection and repair result validation are unchanged. Everything else that reads `action.mode` for a repair keeps `work`: `work_model` selection, usage records, setup and check handling.

Update the docs that list the `{mode}` values `README.md` near "`{mode}` and `{id}` become `work` or `review`": add `repair` for an error ticket. `docs/plan/next-action-and-runner.md` has no value list: add one line to its Agent command section saying the same.

Files: `src/chitty/run.py`, `README.md`, `docs/plan/next-action-and-runner.md`; tests in a new `tests/test_property_render_command.py` (Hypothesis) and a fake-agent test in a new `tests/test_run_repair_mode.py`.

Out of scope: missing-branch recovery (`TASK-326`), and the continuation prompt for a repair session.

## Acceptance Criteria

- [x] Hypothesis property in `tests/test_property_render_command.py`: for any generated list of words (free text, some containing `{mode}`, `{id}` or `{prompt}` zero or more times, none starting with `~`), any mode from `work`, `review`, `repair`, any generated ticket ID, and generated prompt text that may itself contain `{mode}`, `{id}` or `{prompt}`, `render_command` returns one word per input word, equal to the input with `{mode}`, `{id}` replaced and then `{prompt}` replaced, so placeholder text from the prompt stays literal; words without placeholders are unchanged. Example tests: `~/x` expands to the home directory, `a~b` is unchanged.
- [x] Fake-agent tests in `tests/test_run_repair_mode.py`, reusing the argv-logging `FAKE_AGENT` template from `tests/test_run_continue.py`: with `agent_command = "<fake> {mode} {id}"`, `chitty run --errors` on an `error` ticket passes exactly `repair` and the ticket ID; `chitty run` on a `todo` ticket passes `work`, and on a `review` ticket `review`. With a `{prompt}` command, the repair run passes one argument equal to `guide("repair", <ID>)`. The `{mode} {id}` repair case fails before the change by assertion (it receives `work`). `make check` passes.

## Plan

Extract per-word command substitution into render_command(words, mode, ticket_id, prompt), preserving expansion and replacement order. Pass repair mode only to command rendering for error tickets while retaining repair guide selection and work-mode action semantics. Add property and fake-agent regression tests, update both docs, then run format/check and commit.

## Notes

The repair-mode regression assertion was run with command_mode temporarily set to action.mode and failed as expected: argv was [work, TASK-1], not [repair, TASK-1]. Restored the fix and verified the tests pass. The first review-mode test setup lacked the branch required by review preparation; creating the ticket branch resolved it.

Review failed (tests): Both criteria need effective coverage before review can pass. These findings are new; there are no earlier review failures.
1: fail - The Hypothesis strategy uses only arbitrary text, without generating placeholder-bearing words or prompts. Running the property with render_command replaced by an identity function printed `identity mutation passed: True`; explicitly generate placeholders and verify substitution and prompt literalness.
2: fail - The mode tests inherit a command containing `{prompt}` and compare only the first two arguments, rather than configuring `<fake> {mode} {id}` and asserting the exact argv. The prompt fake writes literal backslash-n characters instead of newlines and its assertion is not observed: running the test with the rendered prompt replaced by `WRONG` printed `wrong-prompt mutation passed: True`. Make the fake executable and assert its recorded exact single argument and successful repair. The repair mode regression itself is effective: forcing work printed an assertion failure showing `[work, TASK-1]` versus `[repair, TASK-1]`. `make format && make check` passed, including 597 tests.

Strengthened Hypothesis generation to ensure placeholder-bearing command words and prompts are exercised; the earlier logged pre-fix regression confirmed repair argv was work instead of repair.

Reviewed: Earlier test-coverage findings are resolved.
1: pass - `make format && make check` passed 597 tests; replacing `render_command` with identity made the property fail on `{mode}` versus `work`. Tilde examples pass.
2: pass - `make format && make check` passed 597 tests. Forcing repair mode to `work` made the fake-agent test fail with `[work, TASK-1]` versus `[repair, TASK-1]`; replacing the prompt with `WRONG` made the prompt test fail with `[[WRONG]]` versus the repair guide. Exact work, review and repair argv tests pass.

## Summary

Strengthened placeholder property and fake-agent regressions after review feedback. Verified with make format && make check (597 tests pass). Prompt fake asserts exact repair guide argv and completes repair. No known follow-ups.

## History

- 2026-11-13T23:27:52Z mellow-umber-lapwing → backlog
- 2026-11-13T23:28:22Z mellow-umber-lapwing: changed description
- 2026-11-14T09:23:14Z mellow-umber-lapwing: changed title, description, acceptance criteria
- 2026-11-14T09:23:14Z mellow-umber-lapwing backlog → planning
- 2026-11-14T09:23:18Z mellow-umber-lapwing: changed owner
- 2026-11-14T09:23:18Z mellow-umber-lapwing planning → cold-read
- 2026-11-14T09:27:53Z mellow-umber-lapwing cold-read → planning
- 2026-11-14T09:27:55Z mellow-umber-lapwing planning → cold-read
- 2026-11-14T09:32:00Z mellow-umber-lapwing: changed acceptance criteria
- 2026-11-14T09:32:00Z mellow-umber-lapwing cold-read → planning
- 2026-11-14T09:32:03Z mellow-umber-lapwing planning → cold-read
- 2026-11-14T09:35:15Z mellow-umber-lapwing: changed owner
- 2026-11-14T09:35:15Z mellow-umber-lapwing cold-read → planning
- 2026-11-16T16:58:06Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T16:58:32Z open-russet-eel: changed owner
- 2026-11-16T16:58:32Z open-russet-eel planning → cold-read
- 2026-11-16T17:03:32Z open-russet-eel: changed description, acceptance criteria
- 2026-11-16T17:03:32Z open-russet-eel cold-read → planning
- 2026-11-16T17:03:34Z open-russet-eel: changed owner
- 2026-11-16T17:03:34Z open-russet-eel planning → todo
- 2026-11-17T17:10:58Z sunny-white-quail todo → doing
- 2026-11-17T17:11:15Z sunny-white-quail: wrote the plan
- 2026-11-17T17:16:07Z sunny-white-quail: changed notes, summary; ticked acceptance criteria
- 2026-11-17T17:16:07Z sunny-white-quail doing → review
- 2026-11-17T17:18:35Z vivid-dusky-eel: changed acceptance criteria, notes
- 2026-11-17T17:18:35Z vivid-dusky-eel review → doing
- 2026-11-17T17:28:17Z sunny-indigo-ibis: changed notes, summary; ticked acceptance criteria
- 2026-11-17T17:28:17Z sunny-indigo-ibis doing → review
- 2026-11-17T17:30:41Z honest-white-zander: changed notes; ticked acceptance criteria
- 2026-11-17T17:30:41Z honest-white-zander review → done
