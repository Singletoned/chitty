---
title: Retire the Chitty Pi extension
status: done
labels:
  - needs-minor
depends_on:
  - TASK-320
  - TASK-321
parent: TASK-275
created: 2026-11-11
---

## Description

Remove the bundled Pi extension and its interactive commands, startup flags and usage-file writer without replacements, once `chitty init` no longer installs it. Update current setup guidance, generated examples and documentation to use a `{prompt}` runner command instead of extension flags. Update or remove remaining extension-specific tests, but preserve unrelated Node tooling including Prettier. Do not edit `chitty.toml` on a ticket branch; its local `pi-tui` migration is in `TASK-278`. Historical tickets need not be rewritten. `chitty run` must continue to pass `CHITTY_ACTOR` to descendants: add a fake agent and child process regression without starting a real agent session. No property is needed for fixed documentation text; enumerate changed examples. Write tests first and record failure without the change.

## Acceptance Criteria

- [x] The bundled extension and its extension-only tests are removed; current generated examples and guidance use `{prompt}` without extension flags. A generated-example regression test fails before the change.
- [x] A fake `chitty run` agent and its child inherit the same `CHITTY_ACTOR`; demonstrate the test catches removal of runner actor propagation by mutation. `make check` passes.

## Plan

Add regression coverage first for generated agent examples and CHITTY_ACTOR inheritance through a fake run agent/child, verifying the tests fail against current behavior (including mutation of actor propagation). Then remove the bundled Pi extension and extension-only tests, update current setup guidance/examples to {prompt} commands, and remove extension-specific CLI startup behavior/tests while retaining unrelated Node/Prettier tooling. Run make format and make check, inspect the diff, commit implementation changes with Task: TASK-279, and report verified criteria.

## Notes

Possible starting point: ticket files at `refs/cold-read/TASK-279/1`, after prerequisites; inspect with `git show refs/cold-read/TASK-279/1:<path>`. Check against the current criteria; do not trust it. The ref includes trial prerequisite commits.

The extension-based repository command was removed in `c2eae4b`; the human trials in `TASK-278` are independent of extension removal.

Regression-first evidence: tests.test_pi_retirement failed before changing generated examples because the example still contained extension flags. The fake-agent actor test passed normally and failed when I temporarily removed run_actor assignment, confirming it catches lost CHITTY_ACTOR propagation. make format && make check passed: 577 Python tests, Ruff and Pyright; the extension-only Node test was removed while npm ci and pinned Prettier remain. chitty fix passed; implementation committed as 8a74ebf (Task: TASK-279).

Reviewed:
1: pass - Complete diff removes bundled extension and tests; examples enumerated in README.md, docs/plan/config.md, docs/plan/next-action-and-runner.md, src/chitty/roles/setup.md, src/chitty/config.py, src/chitty/store.py and src/chitty/run.py use {prompt}. The generated-example test passed in make check and failed against the main-branch _add_missing_settings with AssertionError showing the old extension command.
2: pass - make format && make check passed 577 tests, Ruff and Pyright. The fake-agent and child actor test passed in make check; temporarily removing runner CHITTY_ACTOR assignment made that test fail, printing TASK-1: todo → error instead of TASK-1: doing → blocked. Restored the runner afterward.

## Summary

Handoff: removed the bundled Pi extension, usage writer and extension-only tests; updated generated/default setup examples, guidance and docs to use pi -p {prompt}, retaining manual cleanup guidance for existing installations. Added generated-example regression and fake-run-agent plus child-process CHITTY_ACTOR regression. Verification: generated test failed before the change; actor test failed under propagation-removal mutation; make format && make check passed (577 Python tests, Ruff, Pyright); chitty fix passed. Commit: 8a74ebf. No follow-ups.

## History

- 2026-11-11T13:21:35Z vivid-yellowhammer → backlog
- 2026-11-13T22:14:12Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:14:12Z mellow-umber-lapwing backlog → planning
- 2026-11-13T22:14:35Z mellow-umber-lapwing: changed title, description, acceptance criteria
- 2026-11-13T22:14:36Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:16:03Z mellow-umber-lapwing: changed description, acceptance criteria
- 2026-11-13T22:16:03Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:16:06Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:17:01Z mellow-umber-lapwing: changed description
- 2026-11-13T22:17:01Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:17:02Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:19:36Z mellow-umber-lapwing: changed description
- 2026-11-13T22:19:36Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:19:38Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:23:01Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:23:01Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:24:52Z mellow-umber-lapwing: changed dependencies, description, acceptance criteria
- 2026-11-13T22:44:35Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:44:35Z mellow-umber-lapwing planning → cold-read
- 2026-11-13T22:51:59Z mellow-umber-lapwing: changed notes
- 2026-11-13T22:51:59Z mellow-umber-lapwing cold-read → planning
- 2026-11-13T22:52:01Z mellow-umber-lapwing: changed owner
- 2026-11-13T22:52:01Z mellow-umber-lapwing planning → todo
- 2026-11-13T23:23:50Z mellow-umber-lapwing: changed dependencies, notes
- 2026-11-16T11:02:33Z intrepid-maroon-kestrel todo → doing
- 2026-11-16T11:02:49Z intrepid-maroon-kestrel: wrote the plan
- 2026-11-16T11:11:55Z intrepid-maroon-kestrel: changed notes, summary; ticked acceptance criteria
- 2026-11-16T11:11:55Z intrepid-maroon-kestrel doing → review
- 2026-11-16T11:14:13Z intrepid-white-zander: changed notes; ticked acceptance criteria
- 2026-11-16T11:14:13Z intrepid-white-zander review → done
