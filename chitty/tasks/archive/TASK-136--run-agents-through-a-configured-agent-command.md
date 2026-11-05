---
title: Run agents through a configured `agent_command`
status: done
priority: high
depends_on:
  - TASK-126
parent: TASK-106
created: 2026-11-04
---

## Description

`chitty run` has `pi` written into it. Which agent runs is a choice that will change, with token efficiency the likely driver, so it belongs in configuration. Moving it also solves the original problem: workers and reviewers are short-lived, one ticket per session, yet start with everything the person has installed, such as `pi-observational-memory` and `pi-subagent`. The command can now say exactly what to load, and Chitty does not need to know what an extension is.

Add `agent_command` to `chitty.toml`, for example:

```toml
agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts --chitty-{mode} {id}"
```

`chitty run` runs it in the ticket's worktree with inherited streams. Parse it with `shlex.split` with no shell, as `setup` is. Then, in each word, apply `os.path.expanduser`, because without a shell nothing else would, so only a word starting with `~` expands. Then use `str.replace` for `{mode}` (`work` or `review`) and `{id}`: not before the split, where a value could change the words, and not `str.format`, which breaks on other braces. Arguments given to `chitty run` go after it, with no `--`, as `TASK-126` does now.

There is no default, so no agent is favoured. This deliberately breaks `chitty run` in a repository that has not set it, loudly and before anything changes. All validation goes in the `TASK-126` preflight, before any claim or worktree, not in a `config.py` validator, because only `chitty run` needs it and a bad value should not stop `chitty list`. Each of these is an error naming the setting: unset or blank, which also shows an example; unbalanced quotes; missing `{mode}` or `{id}`, because the agent could not know what to do; and a first word that contains a slash but is not absolute, because the preflight and the agent run in different directories. The preflight's `shutil.which("pi")` checks the command's first word instead. Replace `pi` in the other messages in `src/chitty/run.py` with the word "agent" or the command. The `chitty.toml` template has a commented example; existing repositories get only that. Also update the mentions of Pi at `README.md` line 54 and the `chitty run` section, `PLAN.md`'s `launches pi --chitty-<mode> ID` line, and the template's "before Pi starts" comment on `setup`. Most run tests in `tests/test_next.py` fake an agent named `pi`, and will need `agent_command` in their configuration.

This repository sets the following, by the human's decision on 2026-11-04 that agents keep `context-mode`, which keeps large command output out of a worker's context:

```toml
agent_command = "pi --no-extensions -e ~/.pi/agent/extensions/chitty.ts -e ~/.pi/agent/npm/node_modules/context-mode/build/adapters/pi/extension.js --chitty-{mode} {id}"
```

Checked on 2026-11-04: a real Pi session started with those two `-e` paths listed the `ctx_` tools and no `subagent` tool. Do not use `-e npm:context-mode`: that runs an npm install into `~/.pi/agent/tmp`, including install scripts, rather than using the installed copy. `pi -ne -e <missing file> --help` still exits 0, so check what a real session does with a missing path and record it; if Pi fails, `chitty run` already reports the status.

This ticket cannot start until `TASK-126` lands, because `main` has neither the preflight nor the forwarding.

Out of scope: `chitty init` installing the Pi extension, which stays and does nothing when Pi is absent; `CHITTY_PI_SESSION_ID` in `run`, and the fact that only the Pi extension holds the worker and reviewer prompts, which are both for the ticket making another agent work.

## Acceptance Criteria

- [x] A test with a fake agent that records its arguments and directory shows work and review sessions started in the ticket's worktree with `{mode}` and `{id}` replaced, a leading `~` expanded, and arguments given to `chitty run` after them
- [x] No test or code path in `src/chitty/run.py` assumes the agent is `pi`, shown by the tests above using an agent with a different name
- [x] Real `chitty run` work and review sessions are checked to have `ctx_` tools, no `subagent` tool and no `Observational memory` output, with `AGENTS.md` still loaded, and the result, including what a missing `-e` path does, is recorded in a ticket note
- [x] Tests show `agent_command` unset, blank, with unbalanced quotes, missing `{mode}` or `{id}`, with a relative first word, and with a first word not on `PATH` each failing with a message naming the setting, with no claim and no worktree created
- [x] `README.md` and `PLAN.md` describe `agent_command`, this repository sets it as above, the `chitty.toml` template has a commented example, a test shows `chitty init` adding it to an existing repository only as a comment, and `__version__` is bumped above `main`'s

## Plan

Add an optional `agent_command` config field and validate/expand it only in `chitty run` after setup refresh. Replace the hard-coded Pi launch with the parsed command, preserving argument forwarding and loud failures. Extend run/config/init tests, update templates and documentation, configure this repository, bump the version, then run focused tests and `make check` before verifying each criterion.

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the helper the ticket named was private and returned more than a path, so a small public one is specified, with an absolute path. Ticket cannot start before `TASK-126`, now stated. `PI_CODING_AGENT_DIR` pointing at a missing directory, now covered by the message. Criterion 5 now covers both modes and context files and skills, and a ticket note is where the result goes. The fake `pi` must record its arguments, because the ones in `tests/test_next.py` ignore them. Found while checking its report, not by it: the ticket put the missing-file check in `_preflight`, which runs before `refresh_setup`, so it would have refused what the refresh was about to repair; the check now follows the refresh, with a test. Verified by running real `pi --help`: a forwarded `-e` after `--chitty-work` is loaded under `--no-extensions`. Rejected: its finding that `task-126` drops `refresh_setup`, because that branch predates `TASK-134` and its worker is already told to keep the call when rebasing. Checking the file's content, because `refresh_setup` already runs `init_repo`, which refuses a locally edited copy loudly. A criterion for dropping `packages` from `settings.json`, because criterion 5 sees it directly. A criterion for built-in compaction, because a short session may never compact and it is Pi's own behaviour; if it proves wrong, the usage log will show it. `HOME` unset and a symlinked agent directory, because the existing `pi_settings_path` decides both, and Pi fails loudly on a bad path. Review-mode tests needing a ticket in review, which is ordinary test setup. `README.md` lines 107-109 stay true for hand-started `pi`, so criterion 4 means making clear they do not apply to `chitty run`, not deleting them.

Correction to the note above: criteria were renumbered, so the `README.md` point refers to criterion 3 and the real-session points refer to criterion 5.

Changed 2026-11-04: the human decided agents keep `context-mode`. This replaces "add no setting": forwarding by hand on every run would not be automated, and a machine path does not belong in a committed `chitty.toml`, so the setting holds package names. Not cold-read again: the new behaviour was tried against real Pi, and the rest of the ticket is unchanged. Criteria were renumbered again, so earlier notes' numbers are out of date.

Rewritten 2026-11-04 at the human's direction: Chitty must not be tied to Pi, and the human suggested a config option for the agent command. This replaces the hard-coded Pi flags and the `agent_packages` setting, neither of which has been built, along with the missing-extension check, which was Pi-specific. Earlier notes' criterion numbers and helper details no longer apply.

Cold read of the rewrite by a fresh Sonnet subagent, 2026-11-04. Fixed: `str.replace` after the split; validation in the preflight, not `config.py`; `~` expanded only at the start of a word; no `--`; unbalanced quotes; a blank value; a relative first word, because `shutil.which` and the agent would resolve it from different directories (a repository script can use an absolute path or `PATH`, and this is cheap to loosen); and "as `setup` does", which was wrong, since `setup`'s error shows no example. Also added a test for the `chitty init` comment and the documentation locations. I changed "neither placeholder" to requiring both myself, because a command without `{mode}` cannot tell work from review. Rejected: its finding that this repository has no `setup` on `task-126`, which is wrong: `git show task-126:chitty.toml` has `setup = "make install"`. Landing breaking repositories with no setting, because that is what having no default means, and it fails loudly with an example. New tests for inherited streams, exit status and interrupts, because the existing run tests cover them and only need the setting. `{id}` or `{mode}` in the first word, because the `PATH` check catches it. `~user`, because `expanduser` handles it. `[tool.chitty]` in `pyproject.toml`, because the setting is read through the same config. Stale `refresh_setup` notes, because the rewrite's note says earlier details no longer apply, and the worker keeps that call by `TASK-126`'s instructions. The version number, because "above `main`'s" already covers it. Still five criteria.

Watch for `TASK-137`: adding `agent_command` to this repository's `chitty.toml` on the branch stops the global `chitty` working in its worktree.

From the last `TASK-126` review: with a relative `PATH` entry, the preflight finds the agent from the main checkout but the launch runs in the worktree, so it fails with a traceback after the claim. Keep a loud `ChittyError` for `FileNotFoundError` at launch, which that branch removed, and resolve the first word to an absolute path in the preflight, so both use the same executable.

Raised to high on 2026-11-04: `TASK-155`, which the human made high priority, needs it.

Verification: a temporary Git repository ran real `chitty run` work and review sessions with this repository’s configured command; both replied `agent started`, and the ticket worktree contained `AGENTS.md` with the Chitty guide. A real Pi invocation with the two configured extensions successfully called `ctx_stats` and reported `ctx_stats available; subagent unavailable.` Neither session emitted `Observational memory`. A missing `-e /definitely-not-present/chitty.ts` printed `Failed to load extension ... Extension path does not exist` but exited `0` under `--help`; `chitty run` reports a non-zero agent exit status normally. `make check` passed after the implementation.

Re-checked all five criteria against the focused tests, real configured-agent work/review sessions, documentation/configuration changes, version bump, and final `make check`; ready for independent review.

Reviewed: independently checked all five criteria: configured-command parsing, validation and launch behavior; distinct fake-agent work/review coverage; documented real-session evidence; init/template/docs/version changes. Ran make check (ruff, pyright, 228 Python tests, 27 Node tests).

## History

- 2026-11-04T09:25:40Z lively-panda → todo
- 2026-11-04T09:27:11Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T09:27:20Z lively-panda: changed notes
- 2026-11-04T09:31:38Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T09:38:00Z lively-panda: changed title, description, acceptance criteria, notes
- 2026-11-04T09:40:59Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T09:45:42Z lively-panda: changed priority
- 2026-11-04T09:46:24Z lively-panda: changed notes
- 2026-11-04T14:36:51Z mellow-newt: changed notes
- 2026-11-04T15:38:30Z mellow-newt: changed priority, notes
- 2026-11-04T16:06:15Z tidy-marten todo → doing
- 2026-11-04T16:08:32Z tidy-marten: wrote the plan
- 2026-11-04T16:24:52Z tidy-marten: changed notes
- 2026-11-04T16:24:53Z tidy-marten: ticked acceptance criteria
- 2026-11-04T16:27:29Z tidy-marten: changed notes
- 2026-11-04T16:27:29Z tidy-marten doing → review
- 2026-11-04T17:20:28Z open-crane: changed notes
- 2026-11-04T17:20:28Z open-crane review → done
- 2026-11-05T14:44:54Z vivid-wren done → archived
