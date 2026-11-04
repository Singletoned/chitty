---
title: Start `chitty run` agents with only the Chitty extension
status: todo
priority: high
depends_on:
  - TASK-126
parent: TASK-106
created: 2026-11-04
---

## Description

Workers and reviewers are short-lived, one ticket per session, but `chitty run` starts Pi with everything the person has installed: `pi-observational-memory`, `context-mode`, `pi-subagent`, `planning.ts` and more. That spends tokens on memory a throwaway session will never reuse, and adds tools and hooks the ticket did not ask for. A `TASK-132` worker used `pi-subagent` for a cold read that was not its job, and it failed twice.

Have `chitty run` start Pi as `pi --no-extensions -e <agent dir>/extensions/chitty.ts --chitty-<mode> <ID>`. Checked on 2026-11-04: `pi -ne -e ~/.pi/agent/extensions/chitty.ts --help` lists only the two Chitty flags, so this drops discovered extensions and those from `packages` in `settings.json`. Pi keeps its built-in compaction, skills and context files.

Add a small public helper in `src/chitty/actor.py` returning the extension's absolute path, built from `pi_settings_path(...).parent`, and have `_pi_extension_files` use it. That private function does not fit as it is: it also reads the shipped source and returns `None` when the agent directory is absent. Only one path helper means `PI_CODING_AGENT_DIR` is honoured in the same way by both. Change the call in `src/chitty/run.py` as it stands after `TASK-126`, which forwards extra arguments to Pi. That forwarding is the way to add one back, as in `chitty run -e ./search.ts`, so add no setting.

This ticket cannot start until `TASK-126` lands, because `main` has neither the forwarding nor the preflight.

Check that the file exists straight after `repo.refresh_setup()`, not in `_preflight`: the refresh, from `TASK-134`, is what installs a missing extension, and it runs after the preflight, so checking earlier would refuse a repository the refresh was about to repair. It must still come before any claim or worktree. Existence is all it checks. If the file is missing, fail with a message naming the expected path and `chitty init`, and saying that `init` needs Pi's agent directory to exist.

Out of scope: `pi` started by hand, which still loads everything; other harnesses; a Chitty setting listing extensions.

## Acceptance Criteria

- [ ] A test with a fake `pi` shows work and review sessions both started with `--no-extensions` and `-e` naming the extension under `PI_CODING_AGENT_DIR`, plus the `--chitty-<mode>` flag and ticket ID
- [ ] A test shows arguments given to `chitty run` still reach `pi` after those flags
- [ ] `README.md` and `PLAN.md` say which extensions agents get and how to add one, and `README.md` no longer implies `context-mode` runs in `chitty run` sessions
- [ ] A test shows a missing extension file failing with a message naming the path and `chitty init`, with no claim and no worktree created; another shows the refresh installing a missing extension so the run goes ahead
- [ ] Real `chitty run` work and review sessions are checked to have no `ctx_` or `subagent` tools and no `Observational memory` output, with `AGENTS.md` and skills still loaded, and the result is recorded in a ticket note

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the helper the ticket named was private and returned more than a path, so a small public one is specified, with an absolute path. Ticket cannot start before `TASK-126`, now stated. `PI_CODING_AGENT_DIR` pointing at a missing directory, now covered by the message. Criterion 5 now covers both modes and context files and skills, and a ticket note is where the result goes. The fake `pi` must record its arguments, because the ones in `tests/test_next.py` ignore them. Found while checking its report, not by it: the ticket put the missing-file check in `_preflight`, which runs before `refresh_setup`, so it would have refused what the refresh was about to repair; the check now follows the refresh, with a test. Verified by running real `pi --help`: a forwarded `-e` after `--chitty-work` is loaded under `--no-extensions`. Rejected: its finding that `task-126` drops `refresh_setup`, because that branch predates `TASK-134` and its worker is already told to keep the call when rebasing. Checking the file's content, because `refresh_setup` already runs `init_repo`, which refuses a locally edited copy loudly. A criterion for dropping `packages` from `settings.json`, because criterion 5 sees it directly. A criterion for built-in compaction, because a short session may never compact and it is Pi's own behaviour; if it proves wrong, the usage log will show it. `HOME` unset and a symlinked agent directory, because the existing `pi_settings_path` decides both, and Pi fails loudly on a bad path. Review-mode tests needing a ticket in review, which is ordinary test setup. `README.md` lines 107-109 stay true for hand-started `pi`, so criterion 4 means making clear they do not apply to `chitty run`, not deleting them.

Correction to the note above: criteria were renumbered, so the `README.md` point refers to criterion 3 and the real-session points refer to criterion 5.

## History

- 2026-11-04T09:25:40Z lively-panda → todo
- 2026-11-04T09:27:11Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T09:27:20Z lively-panda: changed notes
