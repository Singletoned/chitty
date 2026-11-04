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

Workers and reviewers are short-lived, one ticket per session, but `chitty run` starts Pi with everything the person has installed: `pi-observational-memory`, `pi-subagent`, `planning.ts` and more. That spends tokens on memory a throwaway session will never reuse, and adds tools and hooks the ticket did not ask for. A `TASK-132` worker used `pi-subagent` for a cold read that was not its job, and it failed twice.

Have `chitty run` start Pi as `pi --no-extensions -e <agent dir>/extensions/chitty.ts [-e <package extension>...] --chitty-<mode> <ID>`. Checked on 2026-11-04: `pi -ne -e ~/.pi/agent/extensions/chitty.ts --help` lists only the two Chitty flags, so this drops discovered extensions and those from `packages` in `settings.json`. Pi keeps its built-in compaction, skills and context files.

Add a small public helper in `src/chitty/actor.py` returning the extension's absolute path, built from `pi_settings_path(...).parent`, and have `_pi_extension_files` use it. That private function does not fit as it is: it also reads the shipped source and returns `None` when the agent directory is absent. Only one path helper means `PI_CODING_AGENT_DIR` is honoured in the same way by both. Change the call in `src/chitty/run.py` as it stands after `TASK-126`, which forwards extra arguments to Pi. That forwarding is the way to add one for a single run, as in `chitty run -e ./search.ts`.

Add an optional `agent_packages` list to `chitty.toml`, with no default, so other people's repositories get only the Chitty extension. This repository sets `agent_packages = ["context-mode"]`, by the human's decision on 2026-11-04: it keeps large command output out of a worker's context. The template shows it as a commented example, as it does `setup`. Each name resolves to `<agent dir>/npm/node_modules/<name>`, adding one `-e` with an absolute path for each entry in that package's `package.json` `pi.extensions`; for `context-mode` that is `build/adapters/pi/extension.js`. Do not pass `-e npm:<name>`: checked on 2026-11-04, that runs an npm install into `~/.pi/agent/tmp`, including install scripts, rather than using the installed copy. With the path, a real Pi session listed the `ctx_` tools. A listed package that is not installed, or has no `pi.extensions`, fails loudly at the same point as a missing Chitty extension.

This ticket cannot start until `TASK-126` lands, because `main` has neither the forwarding nor the preflight.

Check that the file exists straight after `repo.refresh_setup()`, not in `_preflight`: the refresh, from `TASK-134`, is what installs a missing extension, and it runs after the preflight, so checking earlier would refuse a repository the refresh was about to repair. It must still come before any claim or worktree. Existence is all it checks. If the file is missing, fail with a message naming the expected path and `chitty init`, and saying that `init` needs Pi's agent directory to exist.

Out of scope: `pi` started by hand, which still loads everything; other harnesses; packages installed anywhere but Pi's global `npm` directory; loading a package's skills, which `-e` does not do and `context-mode`'s tools do not need.

## Acceptance Criteria

- [ ] A test shows a missing extension file failing with a message naming the path and `chitty init`, with no claim and no worktree created; another shows the refresh installing a missing extension so the run goes ahead
- [ ] A test with a fake `pi` that records its arguments shows work and review sessions both started with `--no-extensions`, `-e` naming the extension under `PI_CODING_AGENT_DIR`, and the `--chitty-<mode>` flag and ticket ID, with arguments given to `chitty run` after them
- [ ] A test shows `agent_packages` adding one `-e` for each `pi.extensions` entry, and an uninstalled package or one without `pi.extensions` failing with no claim and no worktree created
- [ ] `README.md` and `PLAN.md` say which extensions agents get and how to add one; this repository sets `agent_packages`, the `chitty.toml` template has a commented example, and `__version__` is bumped above `main`'s
- [ ] Real `chitty run` work and review sessions are checked to have `ctx_` tools, no `subagent` tool and no `Observational memory` output, with `AGENTS.md` and skills still loaded, and the result is recorded in a ticket note

## Notes

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: the helper the ticket named was private and returned more than a path, so a small public one is specified, with an absolute path. Ticket cannot start before `TASK-126`, now stated. `PI_CODING_AGENT_DIR` pointing at a missing directory, now covered by the message. Criterion 5 now covers both modes and context files and skills, and a ticket note is where the result goes. The fake `pi` must record its arguments, because the ones in `tests/test_next.py` ignore them. Found while checking its report, not by it: the ticket put the missing-file check in `_preflight`, which runs before `refresh_setup`, so it would have refused what the refresh was about to repair; the check now follows the refresh, with a test. Verified by running real `pi --help`: a forwarded `-e` after `--chitty-work` is loaded under `--no-extensions`. Rejected: its finding that `task-126` drops `refresh_setup`, because that branch predates `TASK-134` and its worker is already told to keep the call when rebasing. Checking the file's content, because `refresh_setup` already runs `init_repo`, which refuses a locally edited copy loudly. A criterion for dropping `packages` from `settings.json`, because criterion 5 sees it directly. A criterion for built-in compaction, because a short session may never compact and it is Pi's own behaviour; if it proves wrong, the usage log will show it. `HOME` unset and a symlinked agent directory, because the existing `pi_settings_path` decides both, and Pi fails loudly on a bad path. Review-mode tests needing a ticket in review, which is ordinary test setup. `README.md` lines 107-109 stay true for hand-started `pi`, so criterion 4 means making clear they do not apply to `chitty run`, not deleting them.

Correction to the note above: criteria were renumbered, so the `README.md` point refers to criterion 3 and the real-session points refer to criterion 5.

Changed 2026-11-04: the human decided agents keep `context-mode`. This replaces "add no setting": forwarding by hand on every run would not be automated, and a machine path does not belong in a committed `chitty.toml`, so the setting holds package names. Not cold-read again: the new behaviour was tried against real Pi, and the rest of the ticket is unchanged. Criteria were renumbered again, so earlier notes' numbers are out of date.

## History

- 2026-11-04T09:25:40Z lively-panda → todo
- 2026-11-04T09:27:11Z lively-panda: changed description, acceptance criteria, notes
- 2026-11-04T09:27:20Z lively-panda: changed notes
- 2026-11-04T09:31:38Z lively-panda: changed description, acceptance criteria, notes
