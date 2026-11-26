---
title: Add a validated `priorities` list setting to `chitty.toml`
status: doing
parent: TASK-607
created: 2026-11-23
---

## Description

Part of TASK-607. Decided with the person on 2026-11-23: priorities are an ordered list in `chitty.toml`, highest first, and the empty string marks where tickets with no priority rank, for example `priorities = ["now", "soon", "", "later"]`. This ticket adds only the setting and its validation. Nothing reads it yet: ordering and display are TASK-10037, and write and check validation is TASK-10038.

Setting, in `RepoConfig` (`src/chitty/config.py`): `priorities: list[str]`, default `["high", "medium", "", "low"]`, validated by a `field_validator` like `_job_order`. It raises, so loading the config fails with the usual config error, when:

- the list does not contain exactly one `""`: `priorities must contain "" exactly once, to place tickets with no priority`;
- a name is repeated: `priorities lists '<name>' twice`;
- a name has surrounding whitespace (`name != name.strip()`) or a line break (`len(name.splitlines()) > 1`, so every `str.splitlines` boundary counts): `priority '<name>' must be one word or phrase on one line, without surrounding spaces`.

Docs: in `docs/plan/config.md`, next to the `# job_order` line, add `# priorities = ["high", "medium", "", "low"] # highest first; "" places tickets with no priority`.

Tests, in a new `tests/test_priorities_config.py`, calling `RepoConfig.model_validate` (or `load_repo_config` on a written `chitty.toml`) and asserting each message as a substring of the error:

- The default is `["high", "medium", "", "low"]`.
- Each of these is refused with its message: no `""`, two `""`, `["a", "a", ""]`, `[" a", ""]`.
- Property, with Hypothesis (the repository's property tool, `examples(50)` from `tests/__init__.py`): a name of one to five `string.ascii_letters` with one character from `"\n\r\x0b\x0c\x1c\x1d\x1e\x85  "` inserted at a drawn position gives `[name, ""]`, which is refused with the shared one-line message above. On `main`, `RepoConfig` forbids extra keys, so every refusal fails there with `extra_forbidden` instead of its message, and the default test fails with `AttributeError`.

Out of scope: everything that uses the setting (TASK-10037, TASK-10038), and `chitty init` writing it.

## Acceptance Criteria

- [ ] The default, refusal and line-break property tests in `tests/test_priorities_config.py` pass, and each refusal fails on `main` (record it in a note)
- [ ] `docs/plan/config.md` has the `priorities` line; `make check` passes

## Notes

Split 2026-11-26 at the last worker request: ordering, model and display moved to TASK-10037, write and check validation to TASK-10038.

## History

- 2026-11-23T10:40:39Z witty-russet-gannet → backlog
- 2026-11-23T12:37:51Z witty-russet-gannet: changed title, labels, description, acceptance criteria
- 2026-11-23T12:37:51Z witty-russet-gannet backlog → cold-read
- 2026-11-23T12:38:52Z witty-russet-gannet: changed description, notes
- 2026-11-23T12:38:52Z witty-russet-gannet cold-read → todo
- 2026-11-23T12:55:16Z witty-russet-gannet: changed notes
- 2026-11-23T13:09:00Z calm-teal-yellowhammer todo → doing
- 2026-11-23T13:11:32Z calm-teal-yellowhammer: changed owner, notes
- 2026-11-23T13:11:32Z calm-teal-yellowhammer doing → planning
- 2026-11-23T18:37:59Z witty-yellow-vole: replaced notes; changed owner, description, acceptance criteria
- 2026-11-23T18:38:18Z witty-yellow-vole: changed description
- 2026-11-23T18:38:18Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:41:09Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T18:41:09Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:41:14Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:43:55Z witty-yellow-vole: changed description
- 2026-11-23T18:43:55Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:44:00Z witty-yellow-vole planning → cold-read
- 2026-11-23T18:44:21Z witty-yellow-vole: changed acceptance criteria
- 2026-11-23T18:44:21Z witty-yellow-vole cold-read → planning
- 2026-11-23T18:44:23Z witty-yellow-vole planning → todo
- 2026-11-23T19:07:57Z lively-pearl-eel todo → doing
- 2026-11-23T19:10:32Z lively-pearl-eel: changed owner, notes
- 2026-11-23T19:10:32Z lively-pearl-eel doing → planning
- 2026-11-23T19:27:49Z witty-yellow-vole: changed owner, description
- 2026-11-23T19:28:07Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:37:19Z witty-yellow-vole: changed description, acceptance criteria
- 2026-11-23T19:37:19Z witty-yellow-vole cold-read → planning
- 2026-11-23T19:37:29Z witty-yellow-vole planning → cold-read
- 2026-11-23T19:37:59Z witty-yellow-vole: changed description
- 2026-11-23T19:37:59Z witty-yellow-vole cold-read → planning
- 2026-11-23T19:38:01Z witty-yellow-vole planning → todo
- 2026-11-23T20:06:07Z eager-ebony-quail todo → doing
- 2026-11-23T20:08:38Z eager-ebony-quail: wrote the plan
- 2026-11-23T20:09:16Z eager-ebony-quail: changed owner, notes
- 2026-11-23T20:09:16Z eager-ebony-quail doing → planning
- 2026-11-25T10:38:24Z sunny-hazel-gannet: changed notes
- 2026-11-26T11:41:41Z brisk-bronze-adder: changed notes
- 2026-11-26T11:41:41Z brisk-bronze-adder planning → to-plan
- 2026-11-26T11:41:50Z brisk-bronze-adder to-plan → planning
- 2026-11-26T11:42:12Z brisk-bronze-adder: replaced notes; changed title, labels, owner, description, acceptance criteria; wrote the plan
- 2026-11-26T11:42:12Z brisk-bronze-adder planning → cold-read
- 2026-11-26T11:44:51Z brisk-bronze-adder: changed description
- 2026-11-26T11:44:51Z brisk-bronze-adder cold-read → planning
- 2026-11-26T11:44:55Z brisk-bronze-adder planning → todo
- 2026-11-26T13:15:37Z kind-coral-falcon todo → doing
