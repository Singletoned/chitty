---
title: Property-test `ticket_source` choosing among candidates (rules 4 and 6)
status: review
depends_on:
  - TASK-377
parent: TASK-376
created: 2026-11-18
---

## Description

`TASK-377` builds `ticket_source` in `src/chitty/ticket_source.py` and property-tests rules 1 to 3; the rules are in its description. This ticket replaces the fixed-example tests for rules 4 and 6 in `tests/test_property_ticket_source.py` with properties, reusing that file's `graphs()` (a `Graph` with `ancestors`), `task_ids()`, `ref_maps(task_id, candidate_commits, decoy_commits, with_candidates)`, `decoy_names()`, `current_branches()` and `call()` helpers. Split from `TASK-377` on 2026-11-18, after two reviews rejected fixed examples. Change `src/chitty/ticket_source.py` only if a property finds a bug; then fix it and say so in the notes.

Build inputs whose answer is known by construction, rather than recomputing the rules in the test:

- Chain: draw `main_tip` as a commit index m from 0 to n-1, so a commit lies above it, or `None`, when candidates go on any commit. Place one to four candidates (the local name and remote names) on commits above m, and optionally dropped candidates at or below m. The expected tip is the highest candidate commit above m; the expected name is the local candidate at that commit if there is one, else the remote whose remote name (before its first `/`) sorts first.
- Fork: put every remaining candidate on one arm, so they are comparable, and `main_tip` on the shared chain or on the other arm, so it contains none of them. Expected as for the chain.
- Draw `current_branch` from the local candidate name, `main_branch`, a decoy and `None`. The result is `WORKING_TREE` exactly when `current_branch` is the local candidate name and the local candidate is at the expected tip; otherwise the expected name. Draw a boolean that, when true, builds a remote candidate strictly ahead of a checked-out local one (the result is the remote name).
- Ties: draw a boolean that, when true, puts the local candidate, or two or more remotes, on the expected tip, so that tie-breaking is exercised.
- Rule 6: the same inputs with `changed_on_both` true for the expected name (other names may also be true), also when the rule 4 result would be `WORKING_TREE`: `ChittyError` whose message contains the ticket ID, the expected ref and `main_branch`, each quoted in backticks. With `changed_on_both` true only for other names: the rule 4 result.

Each property asserts a returned value or `ChittyError` specifically. Tests match quoted names, so `task-5` is not found inside `origin/task-5`.

The code already exists, so evidence that the tests catch a wrong implementation comes from mutants run by hand and not committed: each changes `ticket_source` in one way, and the notes record which property failed.

## Acceptance Criteria

- [ ] Properties for rule 4 pass on both graph shapes: the result is `WORKING_TREE` exactly when `current_branch` is the local candidate name and the local candidate is at the expected tip, otherwise the candidate at the expected tip, the local one when it is there, else the remote whose remote name sorts first; generated examples include a remote strictly ahead of a checked-out local candidate
- [ ] Properties for rule 6 pass: with `changed_on_both` true for the expected name, `ChittyError` names the ticket, that ref and `main_branch`, each quoted; with it true only for other names, the result is the rule 4 result
- [ ] The notes name at least three mutants of `ticket_source`, among them remotes winning ties, the wrong remote order, and ignoring `changed_on_both`, each failing a property of this ticket; `make check` passes

## Plan

Replace the fixed rule 4 and 6 examples with shared generated chain/fork inputs: choose main tips, surviving and dropped candidates, decoys, current branches, tie cases, and remote-ahead cases. Compute expected selection from construction and assert both changed-on-both branches. Run properties against temporary mutants for remote tie preference, remote ordering, and ignored changed_on_both; record evidence, then format, check, and commit.

## Notes

Cold read 2026-11-18 outcomes: forced ties so tie mutants die; defined the range of m and the `None` case.

Second cold read 2026-11-18 outcomes: remote-ahead and tie cases forced by drawn booleans; rule 6 wording no longer reads as an error for other names; rule 6 also applies when the result would be `WORKING_TREE`.

Verification: focused property module passes; make check passes (746 tests). Mutant evidence not completed: the required hand-run mutants for remote tie preference, remote ordering, and changed_on_both remain a follow-up, so acceptance criterion 3 is not met.

Review failed (tests): Expand the generated cases and complete the required mutation evidence. These findings are new; there are no earlier review notes.
1: fail - `make check` printed `Ran 746 tests` and `OK`, but inspection of `tests/test_property_ticket_source.py` shows the new selection property always uses `main_tip=None`, places all candidates at the same tip, and uses only the local branch or `None` as current; the separate remote-ahead test also uses `main_tip=None`. Generate chain and fork cases with the specified main tips, dropped and surviving candidates on varied commits, decoys, and all specified current branches; replace the legacy fixed examples. No mutation evidence establishes the new properties fail without correct behavior.
2: fail - `make check` printed `OK`, but the rule 6 properties use only a shared-chain tip with `main_tip=None`, rather than the same generated chain and fork selection inputs required by the ticket. Exercise expected and other changed refs across those inputs, including checkout and remote-ahead cases. No mutation evidence establishes the properties fail without correct behavior.
3: fail - `make check` printed `Ran 746 tests` and `OK`, but the existing verification note explicitly says the three required mutant runs remain outstanding. Run and record the remote-tie, remote-order and ignored-changed-on-both mutants and identify the property each fails.

Updated rule 4 and rule 6 coverage to generate chain/fork candidate layouts, main tips, candidate refs, decoys, current branches, changed-ref errors, and remote-ahead cases. Focused property module passes; make check passes all 743 tests (with the expected Hypothesis warning). Required temporary mutant evidence for remote tie preference, remote ordering, and ignored changed_on_both was not run; acceptance criterion 3 remains incomplete.

Mutation evidence: temporary mutant making remotes win equal-tip ties failed the focused property module (exit 1); temporary mutant reversing remote-name ordering failed it (exit 1); temporary mutant ignoring changed_on_both failed it (exit 1). Mutations were reverted before verification. Final focused property module passes. make check completed: formatting, Ruff, pyright, and all 743 tests pass; command exits non-zero because nested chitty run tests report the existing missing autocommit=true fixture configuration.

Review failed (tests): Complete the generated cases and identify the failing property for each mutant. The earlier review reported inadequate generated layouts and missing mutation evidence; the remaining gaps below are newly identified in the replacement.
1: fail - `uv run python -m unittest tests.test_property_ticket_source` printed `Ran 9 tests` and `OK`, but the generated selection property always forces a tie unless it switches to remote-ahead, so it never exercises a sole local or sole remote candidate, nor a unique local tip ahead of remotes. The description requires one to four candidates and a boolean enabling ties. Generate untied layouts too and replace the three legacy fixed rule 4/6 examples as requested.
2: fail - The same property passes as above, but inherits the missing untied layouts; additionally, in remote-ahead cases it chooses the other changed name from the stale `tips` map after replacing the actual remote map, so that name can be absent rather than another candidate. Exercise actual other candidates as well as expected names on the required layouts.
3: fail - `make check` exited 0 and printed `Ran 743 tests` and `OK`. The mutation note records three module-level failures but does not identify which property failed for each mutant, as required by the description. Record the failing property for each mutant, with evidence that it fails without the corresponding behavior.

Replaced the three legacy fixed examples with generated selection and changed_on_both assertions. Mutation checks were run against tests.test_property_ticket_source.TestTicketSource.test_rules_4_and_6_choose_among_generated_candidates: the local-tie-winner mutant (remotes win ties) failed with an incorrect selected ref; the max-remote-name mutant failed on alpha versus zeta; the ignored-changed_on_both mutant failed because ChittyError was not raised. Each temporary mutation was reverted; ticket_source.py is unchanged.

Verification: focused property module passes (6 tests); formatter, Ruff and pyright pass. make check executes 743 tests but exits non-zero on unrelated tests.test_next.TestNext.test_run_cases: expected exit code 3, got 0. This is the known nested chitty run fixture/configuration mismatch, not caused by TASK-403.

Runner error (check): check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
606 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 740 test suites (740 total tests) across 16 workers
.................................................................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 15:47:31 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.............................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
.......................................................................................F..............................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
.........../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/CLAUDE.md
......Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/.worktrees/task-1...
..TASK-1: doing → review
...no next ticket for --mode work
...../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/CLAUDE.md
...............................................chitty 0.1.31 is out: run uv tool upgrade chitty
................................landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_run_cases (tests.test_next.TestNext.test_run_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-403/tests/test_next.py", line 1847, in test_run_cases
    no_next = self.run_cli("run", exit_code=3)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-403/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 3 : TASK-1: blocked → error
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp82lum__l/repo/.worktrees/task-1...


----------------------------------------------------------------------
Ran 740 tests in 32.960s

FAILED (failures=1)
make: *** [check] Error 1

```

Worktree: `/Users/singletoned/src/singletoned/chitty/.worktrees/task-403`

Error output:
````text
check exited with status 2:
```text
! git grep -nE '^(<<<<<<< |>>>>>>> |=======$)'
uv run ruff format --check .
606 files already formatted
uv run ruff check --no-fix .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
uv run unittest-parallel -s tests -t . --level test
Running 740 test suites (740 total tests) across 16 workers
.................................................................................................................................................................................................................................................................................................................................................................................................................................................━━━━ chitty run · 15:47:31 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━━━ stopped · exit 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.............................................../Users/singletoned/.local/share/uv/python/cpython-3.13.12-macos-aarch64-none/lib/python3.13/contextlib.py:141: HypothesisWarning: subTest per-test-case reporting interacts badly with Hypothesis trying hundreds of test cases, so we disable it for the duration of any test that uses `@given`.
  return next(self.gen)
.......................................................................................F..............................................................Error: `chitty run` configuration is incomplete in chitty.toml:
- `chitty run` requires `autocommit = true` in chitty.toml, so ticket changes reach every branch; `chitty init --autocommit` sets it
.........../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/CLAUDE.md
......Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi93nu2gg/repo/.worktrees/task-1...
..TASK-1: doing → review
...no next ticket for --mode work
...../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpi30xqrjv/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpvu4otiez/repo/CLAUDE.md
../private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpgr9jdq8s/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmps3_d740g/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpv6va_vah/repo/CLAUDE.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpwn3d90q1/repo/CLAUDE.md
./private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/chitty.toml
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/chitty/tasks
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/chitty/human
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/chitty/backlog
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/data/chitty/inbox/repo
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/.gitignore
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/AGENTS.md
/private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmpj85o9ptz/repo/CLAUDE.md
...............................................chitty 0.1.31 is out: run uv tool upgrade chitty
................................landed TASK-1
landed TASK-2
landed TASK-1

======================================================================
test_run_cases (tests.test_next.TestNext.test_run_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-403/tests/test_next.py", line 1847, in test_run_cases
    no_next = self.run_cli("run", exit_code=3)
  File "/Users/singletoned/src/singletoned/chitty/.worktrees/task-403/tests/test_cli.py", line 89, in run_cli
    self.assertEqual(result.exit_code, exit_code, result.output)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 3 : TASK-1: blocked → error
Running check in /private/var/folders/k6/f9sc719s7796fqb92smsvq0r0000gn/T/tmp82lum__l/repo/.worktrees/task-1...


----------------------------------------------------------------------
Ran 740 tests in 32.960s

FAILED (failures=1)
make: *** [check] Error 1

```
````

Reset 2026-11-19: the runner error came from the flaky `tests.test_next.TestNext.test_run_cases`, fixed on `main` in `fe1ef0cd`; back to `review`.

## Summary

Completed generated rule 4 and 6 property coverage; removed three fixed examples. Mutant checks each failed the generated property tests as recorded in Notes, and all mutations were reverted. Focused property suite, formatting, Ruff and pyright pass. make check remains non-zero only for tests.test_next.TestNext.test_run_cases (expected 3, got 0), unrelated to this change. Implementation committed as d82b0f05 and c8a6f0da; ticket is ready for review with the suite failure disclosed.

## History

- 2026-11-18T21:31:03Z lively-quartz-crane → backlog
- 2026-11-18T21:31:17Z lively-quartz-crane: changed acceptance criteria
- 2026-11-18T21:32:12Z lively-quartz-crane backlog → planning
- 2026-11-18T21:32:16Z lively-quartz-crane planning → cold-read
- 2026-11-18T21:35:18Z lively-quartz-crane: changed description, notes
- 2026-11-18T21:35:18Z lively-quartz-crane cold-read → planning
- 2026-11-18T21:37:49Z lively-quartz-crane: changed description, notes
- 2026-11-18T21:37:56Z lively-quartz-crane planning → todo
- 2026-11-19T14:20:34Z quick-ginger-lapwing: changed description
- 2026-11-19T15:22:31Z friendly-russet-urchin todo → doing
- 2026-11-19T15:23:24Z friendly-russet-urchin: wrote the plan
- 2026-11-19T15:26:25Z friendly-russet-urchin: changed notes, summary
- 2026-11-19T15:30:11Z friendly-russet-urchin doing → review
- 2026-11-19T15:33:00Z sunny-silver-ibis: changed acceptance criteria, notes
- 2026-11-19T15:33:00Z sunny-silver-ibis review → doing
- 2026-11-19T15:34:22Z lively-teal-yellowhammer: wrote the plan
- 2026-11-19T15:36:31Z lively-teal-yellowhammer: changed notes
- 2026-11-19T15:38:22Z lively-teal-yellowhammer: changed notes, summary
- 2026-11-19T15:38:25Z lively-teal-yellowhammer doing → review
- 2026-11-19T15:41:05Z rosy-violet-falcon: changed acceptance criteria, notes
- 2026-11-19T15:41:05Z rosy-violet-falcon review → doing
- 2026-11-19T15:46:08Z friendly-coral-dormouse: changed notes, summary
- 2026-11-19T15:46:08Z friendly-coral-dormouse doing → review
- 2026-11-19T15:47:57Z golden-teal-zander: changed notes
- 2026-11-19T15:47:57Z golden-teal-zander review → error
- 2026-11-19T16:02:03Z quick-ginger-lapwing: changed notes
- 2026-11-19T16:02:03Z quick-ginger-lapwing error → review
