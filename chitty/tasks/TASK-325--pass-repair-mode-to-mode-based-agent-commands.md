---
title: Pass repair mode to mode-based agent commands
status: cold-read
owner: open-russet-eel
parent: TASK-318
created: 2026-11-13
---

## Description

`chitty run --errors` repairs a ticket in `error`, but `_agent_command` in `src/chitty/run.py` renders `{mode}` from `action.mode`, which is `work` for a repair. A `{prompt}` command gets the repair guide through a special case (`status == "error"` → `guide("repair", ticket)`), but a `{mode} {id}` command receives `work` and may start an ordinary worker.

Take the substitution out of `_agent_command` into a pure function in `src/chitty/run.py`:

`render_command(words: Sequence[str], mode: str, ticket_id: str, prompt: str) -> tuple[str, ...]`

which replaces `{mode}`, `{id}` and `{prompt}` in each word, as `_agent_command` does today, and expands a leading `~` the same way. `_agent_command` computes the mode as `repair` when the ticket status is `error` and `action.mode` otherwise, and passes it to `render_command`. `NextAction.mode` stays `work | review`. The `{prompt}` path keeps giving the repair guide for an error ticket. Continuation prompts, `--errors` selection and repair result validation are unchanged.

Update the docs that list the `{mode}` values (`README.md` near "`{mode}` and `{id}` become `work` or `review`", and `docs/plan/next-action-and-runner.md`) to include `repair`.

Files: `src/chitty/run.py`, `README.md`, `docs/plan/next-action-and-runner.md`; tests in a new `tests/test_property_render_command.py` (Hypothesis) and a fake-agent test in a new `tests/test_run_repair_mode.py`.

Out of scope: missing-branch recovery (`TASK-326`), and the continuation prompt for a repair session.

## Acceptance Criteria

- [ ] Hypothesis property in `tests/test_property_render_command.py`: for any generated list of words (free text, some containing `{mode}`, `{id}` or `{prompt}` zero or more times, none starting with `~`), any mode from `work`, `review`, `repair`, and generated ticket ID and prompt text without braces, `render_command` returns one word per input word, each equal to the input with every placeholder replaced, and words without placeholders unchanged. A second property: the mode `_agent_command` passes is `repair` exactly when the ticket status is `error`. The second fails before the change.
- [ ] A fake agent, run through `chitty run --errors` with an `agent_command` of `<fake> {mode} {id}`, records the arguments it received: they are `repair` and the error ticket ID. The same run with a `{prompt}` command receives the repair guide (`guide("repair", <ID>)`). A plain `chitty run` of a `todo` ticket with the `{mode} {id}` command still receives `work`. The `{mode} {id}` repair case fails before the change. `make check` passes.

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
