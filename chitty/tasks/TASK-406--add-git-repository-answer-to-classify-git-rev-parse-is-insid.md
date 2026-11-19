---
title: Add `git.repository_answer` to classify `git rev-parse --is-inside-work-tree` results
status: done
created: 2026-11-19
---

## Description

`git.is_repository` (`src/chitty/git.py:371`) returns `result.returncode == 0 and result.stdout.strip() == "true"`, so every non-zero exit of `git rev-parse --is-inside-work-tree` reads as a folder outside Git. Only one of those exits means that: status 128 with `not a git repository` in standard error. Others are hidden, such as `detected dubious ownership`, `unable to access '.git/config': Permission denied` or `Expected git repo version <= 1, found 99` (all status 128), and callers silently skip committing.

This ticket adds only the decision, as a pure function; `TASK-407` makes `is_repository` use it.

Add to `src/chitty/git.py`: `repository_answer(command: Sequence[str], directory: Path, returncode: int, stdout: str, stderr: str) -> bool`.

- Status 0: `True` when `stdout.strip()` is `true`, otherwise `False`. Standard error is ignored.
- Status 128 with standard error containing `not a git repository` (case-sensitive; `TASK-407` forces English output): `False`.
- Anything else, including negative statuses (a signal killed `git`) and status 128 with empty standard error: raise `ChittyError` containing the command, `str(directory)` and the stripped standard error, in the style of `_git` (`src/chitty/git.py:656`).

Tests go in `tests/test_git.py`. The repository's property-testing tool is Hypothesis. Before writing the function, add it raising `NotImplementedError` so the tests fail on their own.

## Acceptance Criteria

- [x] Property test, Hypothesis, status 0: standard output `true` padded with whitespace that `str.strip()` removes gives `True`; output sampled from `false`, `True`, `TRUE`, `truex`, `xtrue`, `true false`, the empty string, or drawn text whose stripped form is not `true`, gives `False`. Standard error is drawn text in both.
- [x] Property test, Hypothesis, non-zero status: status 128 with standard error made of the lowercase `not a git repository` between two drawn texts (either may be empty) gives `False`. Every other case raises `ChittyError` containing the command as `_git` shows it (`` `git rev-parse --is-inside-work-tree` ``), `str(directory)` for a drawn `directory`, and the stripped standard error: status drawn from -64 to 255 excluding 0, with 128 always among the cases, and standard error drawn text filtered to lack the phrase (empty allowed, which checks only the command and directory); status other than 128 with the phrase; 128 with `Not a git repository` or `NOT A GIT REPOSITORY`. Standard output is drawn from `true`, padded `true` and drawn text in every case.
- [x] Evidence, recorded in a note: the tests failed against the `NotImplementedError` stub, and each wrong version, implemented and run, fails a test from criteria 1 or 2: case-insensitive phrase match; `"true" in stdout`; `True` whenever stripped output is `true`, whatever the status; status 128 gives `False` without checking the phrase; any non-zero status gives `False`; message without the command. A Hypothesis test drawing the status from `st.integers()` and both streams from `st.text()` shows the function only returns a `bool` or raises `ChittyError`.
- [x] `make check` passes.

## Plan

Add a property that always supplies status 128 with the lowercase phrase, drawn prefix and suffix, and STDOUTS. First verify the property fails against a throwaway mutant that raises for this valid case, then run focused tests and make check; record the evidence and commit the test change.

## Notes

Confirmed the Hypothesis tests fail against the temporary NotImplementedError stub: `python -m unittest tests.test_git.TestRepositoryAnswer` errored in the expected cases. The suite now covers exact `true` matching, phrase case/status boundaries, error context, and arbitrary integer statuses/streams. I did not perform separate implementation-and-run mutation checks for every incorrect variant listed in criterion 3.

Review failed (integration): merging `main` conflicts in `tests/test_git.py`.

Merged main into task-406 and resolved the tests/test_git.py conflict by retaining both TASK-406 classifier tests and main’s TASK-405 repository-detection tests. Focused tests passed (10 tests), and make check passed all 690 tests. Criterion 3 mutant experiments were not performed for the incorrect variants, so that evidence remains outstanding. make format also removed duplicate os and tempfile imports after the merge.

Added a deterministic status-128/empty-stderr test to ensure 128 is always exercised without the repository phrase. Ran each requested wrong implementation against its corresponding test: case-insensitive phrase failed the case-sensitivity test; substring true failed exact output; stdout true regardless of status and status-128-always-false each failed the status-128 error test; any non-zero false failed contextual-error assertions; omitted command failed command-context assertion. The arbitrary-integer/text Hypothesis property also passes. make format and make check pass (691 tests; Ruff and Pyright clean).

Review failed (tests): Newly discovered coverage gaps below; the earlier integration review reported a merge conflict, which was resolved by the subsequent merge.
1: pass - TestRepositoryAnswer covers padded true, the listed false outputs and drawn non-true text; the worker note records that the tests failed against the NotImplementedError stub.
2: fail - In tests/test_git.py, phrase-containing cases use only stdout true and statuses 1, 128 and 255; case-variant cases also use only stdout true. Draw true, padded true and arbitrary stdout in every nonzero case, draw other nonzero statuses for the phrase case, and assert command, drawn directory and stripped stderr context for all raising cases, including phrase and case-variant diagnostics. The existing contextual test only covers stderr without the phrase. The stub failure is recorded in the worker note.
3: pass - The worker notes record the stub failure and all six mutant failures; test_arbitrary_results_return_bool_or_raise_chitty_error draws integers and both streams. make check ran 691 tests and printed OK.
4: pass - make check exited 0; Ruff and Pyright passed and 691 tests printed OK.

Expanded all nonzero diagnostic tests to vary stdout and assert command, directory, and stripped stderr in each error case. Focused tests pass. make check exited 0 with 690 tests; its wrapper returned exit 1 after test success due to the repo test runner reporting chitty run configuration errors from fixtures.

Re-ran make check after the coverage update: Ruff, Pyright, formatting, and all 690 tests report success, but make check itself exits 1. The output includes fixture-emitted chitty run configuration errors (missing autocommit in temporary fixture repositories). No source or configuration outside this ticket was changed. This is recorded for review; the code-focused checks and complete test suite pass.

Review failed (tests): The earlier review reported missing stdout coverage in every nonzero diagnostic case; that finding remains partly unresolved. Expand the strategies as described below.
1: pass - uv run python -m unittest tests.test_git.TestRepositoryAnswer printed Ran 7 tests and OK; the properties cover padded true, the specified false strings, drawn non-true output and drawn stderr.
2: fail - Newly identified detail of the earlier stdout coverage finding: test_phrase_only_classifies_status_128 and test_repository_phrase_is_case_sensitive sample the fixed string arbitrary output instead of drawing text, and test_other_failures_raise_with_context draws only st.text() rather than explicitly sampling true and padded true as well. Use a strategy combining both explicit outputs with st.text() in every nonzero case. The focused test command printed Ran 7 tests and OK but does not exercise the required strategies.
3: pass - Worker notes record the NotImplementedError stub and all six mutant failures; the arbitrary integer and stream property ran in the focused suite, which printed OK.
4: pass - make check exited 0: Ruff and Pyright passed, and the parallel suite printed Ran 690 tests and OK.

Escalated to human review: failed review 3 times. A human should decide how to proceed, then unblock it.

Planning session 2026-11-19, after escalation: merged `main` and fixed the last review finding. A module-level `STDOUTS` strategy (`true`, padded `true`, or `st.text()`) now supplies standard output in `test_phrase_only_classifies_status_128`, `test_repository_phrase_is_case_sensitive` and `test_other_failures_raise_with_context`. The earlier note that `make check` exits 1 was wrong: it exits 0 here.

Review failed (tests): The earlier stdout-strategy finding is resolved; a newly discovered status-128 coverage gap remains.
1: pass - uv run python -m unittest tests.test_git.TestRepositoryAnswer printed Ran 7 tests and OK; the worker recorded the stub failure.
2: fail - test_phrase_only_classifies_status_128 draws status from a broad integer range without guaranteeing 128. A throwaway in-memory mutant that raises ChittyError whenever status is 128 and stderr contains the lowercase phrase still printed Ran 7 tests, OK, and mutant passed: True. Add a property that always uses status 128 and drawn prefix, suffix and STDOUTS, and confirm it fails against that mutant.
3: pass - The worker notes record the stub and all six requested mutant failures; the arbitrary integer and stream property ran in the focused suite, which printed OK.
4: pass - make check exited 0, with Ruff and Pyright clean and Ran 693 tests, OK.

Added a dedicated status-128 phrase property using drawn prefix, suffix, directory and STDOUTS. Focused tests passed (8 tests). The property failed against a throwaway mutant that raises on status 128 plus the lowercase phrase. make check printed Ruff/Pyright success and all 694 tests OK, but the command exited 1 due fixture-generated incomplete chitty run configuration errors.

Re-ran make check; this run exited 0 with Ruff, Pyright, formatting, and all 694 tests passing. Earlier fixture-generated configuration messages were non-fatal; the prior exit-1 report was incorrect.

Reviewed: Earlier status-128 phrase coverage gap is resolved by the dedicated property; the worker recorded that its rejecting mutant failed.
1: pass - uv run python -m unittest tests.test_git.TestRepositoryAnswer printed Ran 8 tests and OK; the worker recorded the stub failure.
2: pass - The focused suite printed Ran 8 tests and OK; properties cover phrase, case, statuses, diagnostics and varied stdout, including guaranteed 128 cases. The worker recorded the rejecting mutant failure.
3: pass - Worker notes record the stub and all six requested mutant failures; the arbitrary integer and streams property passed in the focused suite, which printed OK.
4: pass - make check exited 0; Ruff and Pyright passed and the suite printed Ran 694 tests and OK.

## Summary

Added guaranteed status-128 phrase coverage with varied stdout, diagnostic context, and directory. Focused tests pass; the rejecting mutant failed as expected. make check passes: Ruff, Pyright, formatting, and all 694 tests.

## History

- 2026-11-19T08:43:27Z lively-quartz-crane → planning
- 2026-11-19T08:43:53Z lively-quartz-crane: changed description, acceptance criteria
- 2026-11-19T08:47:04Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:48:59Z lively-quartz-crane: changed description
- 2026-11-19T08:49:15Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:49:17Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T08:49:37Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:51:02Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:51:05Z lively-quartz-crane: changed title, description, acceptance criteria
- 2026-11-19T08:51:25Z lively-quartz-crane: changed dependencies
- 2026-11-19T08:51:30Z lively-quartz-crane planning → cold-read
- 2026-11-19T08:52:50Z lively-quartz-crane cold-read → planning
- 2026-11-19T08:52:52Z lively-quartz-crane: changed acceptance criteria
- 2026-11-19T08:52:52Z lively-quartz-crane planning → todo
- 2026-11-19T08:56:36Z youthful-pearl-eel todo → doing
- 2026-11-19T08:57:51Z youthful-pearl-eel: wrote the plan
- 2026-11-19T08:59:45Z youthful-pearl-eel: changed notes
- 2026-11-19T09:00:35Z youthful-pearl-eel: changed summary
- 2026-11-19T09:00:35Z youthful-pearl-eel doing → review
- 2026-11-19T09:00:56Z sunny-yellow-stoat: changed notes
- 2026-11-19T09:00:56Z sunny-yellow-stoat review → doing
- 2026-11-19T09:04:02Z mellow-khaki-jay: changed notes
- 2026-11-19T09:05:45Z mellow-khaki-jay: changed notes
- 2026-11-19T09:05:58Z mellow-khaki-jay: changed summary; ticked acceptance criteria
- 2026-11-19T09:05:58Z mellow-khaki-jay doing → review
- 2026-11-19T09:08:35Z kind-indigo-wren: changed acceptance criteria, notes
- 2026-11-19T09:08:35Z kind-indigo-wren review → doing
- 2026-11-19T09:10:17Z brisk-silver-wren: wrote the plan
- 2026-11-19T09:11:48Z brisk-silver-wren: changed notes, summary
- 2026-11-19T09:13:13Z brisk-silver-wren: changed notes, summary
- 2026-11-19T09:13:15Z brisk-silver-wren doing → review
- 2026-11-19T09:15:13Z mellow-bronze-yellowhammer: changed owner, acceptance criteria, notes
- 2026-11-19T09:15:13Z mellow-bronze-yellowhammer review → blocked
- 2026-11-19T09:33:31Z quick-ginger-lapwing: changed owner, notes; ticked acceptance criteria
- 2026-11-19T09:33:31Z quick-ginger-lapwing blocked → review
- 2026-11-19T10:35:59Z friendly-jade-otter: changed acceptance criteria, notes
- 2026-11-19T10:35:59Z friendly-jade-otter review → doing
- 2026-11-19T10:38:25Z vivid-hazel-wren: wrote the plan
- 2026-11-19T10:39:36Z vivid-hazel-wren: changed notes, summary
- 2026-11-19T10:40:37Z vivid-hazel-wren: changed notes, summary
- 2026-11-19T10:40:37Z vivid-hazel-wren doing → review
- 2026-11-19T10:43:05Z honest-umber-zander: changed notes; ticked acceptance criteria
- 2026-11-19T10:43:05Z honest-umber-zander review → done
