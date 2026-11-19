---
title: Move guide rules that code can enforce out of the role guides
status: backlog
created: 2026-11-19
---

## Description

The role guides total about 4,100 words (`plan.md` 1074, `review.md` 885, `cold-read.md` 678, `work.md` 578) and reach every repository. Several rules are already enforced in code and could shrink to a pointer: verdict-line format (`store.py` regex), the third-failure block (`REVIEW_FAILURE_LIMIT`). Others could be enforced: `chitty edit -s review` refusing a dirty worktree or a failing configured check; refusing a branch diff that touches `chitty.toml`, the managed `AGENTS.md` block or `__version__`; checking that branch commits carry `Task: <ID>`; the runner checking the worktree is clean before starting a reviewer; mechanically running new tests against the merge base to show they fail without the change (the main source of `Review failed (tests)`: 31 here, 69 in echonomicon); `chitty check` warning on more than five criteria; deleting stale `refs/cold-read` refs when ticket text changes; removing shell-quoting advice by having text options read stdin or a file. Split into one ticket per rule.

## Notes

Suggestion origin: chitty

## History

- 2026-11-19T20:55:17Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:18Z sunny-white-dormouse: changed notes
