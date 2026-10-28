---
title: Backlog.md import removes imported source files tracked by Git
status: todo
created: 2026-10-28
---

## Description

After a successful import, the Backlog.md source files that were converted still sit in backlog/, so the repo holds duplicate tickets until someone removes them by hand (circuitry's migration stalled at this step). By default, remove every converted source file that Git tracks and that matches HEAD, using git rm in the same commit as the import, so the cutover is one revertible commit. Non-task files that were left are not touched. If any converted file is untracked or has staged or unstaged changes, refuse before writing anything, list those paths, and tell the caller to choose: --remove-source deletes them anyway, --keep-source leaves the whole source in place (today's behaviour). The CLI never prompts, so an agent passes the choice to its human. This reverses the PLAN.md decision that the import leaves source files for a person to delete.

## Acceptance Criteria

- [ ] Clean, tracked converted files are removed with git rm and the deletions land in the import's autocommit (only staged when autocommit is off)
- [ ] Non-task files and anything not converted stay in place and are still reported; backlog/ is removed only if it ends up empty
- [ ] Untracked or dirty converted files make the import fail before any write, naming each path and both flags
- [ ] --remove-source deletes untracked or dirty converted files too; --keep-source leaves the source untouched; passing both is an error
- [ ] A failed import (validation, unresolved references, finalize problems) deletes nothing
- [ ] A repo that is not a Git repository is treated like untracked files
- [ ] Tests cover each case against real temp Git repositories; PLAN.md, README migration section and import --help are updated

## Notes

Suggestion origin: circuitry

Decided with the human: duplicate tickets are worse than deletion, so removing clean, tracked files is the default; Git history is the safety net. We chose fail-with-choices over an interactive prompt so agents never hang.

PLAN.md records the decision. README and import --help still describe the current behaviour (source left in place); update them with the implementation so they never describe behaviour that doesn't exist.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
