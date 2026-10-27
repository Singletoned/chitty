---
title: Fix chitty init in repos with a pyproject.toml
status: done
labels:
  - bug,config
priority: high
created: 2026-10-27
---

## Description

Found trialling a Backlog.md migration on a clone of sump. init_repo (src/chitty/store.py) treats any pyproject.toml as existing chitty config, so in a normal Python repo with no [tool.chitty] init fails with 'no Chitty configuration in <repo>' and nothing can be set up. The upgrade path has related bugs: it decides whether project and archive are set by substring search of the raw file text (every pyproject.toml contains [project], so a missing project key is never added; a comment mentioning archive hides a missing archive key), and it inserts new keys at text.find('[contexts.') / '[tool.chitty.contexts.', which corrupts the file when that marker is absent (find returns -1) and puts keys in the wrong table when another table sits between the settings and the contexts.

## Acceptance Criteria

- [x] In a repo with a pyproject.toml but no [tool.chitty], init creates chitty.toml as for a new repo and leaves pyproject.toml untouched
- [x] Missing settings are detected from the parsed config, not substring search of the file text
- [x] Added settings always land in the top-level table of chitty.toml or in [tool.chitty], whatever the table layout; init never writes a file it cannot re-parse to the same values plus the additions
- [x] Regression tests for each case (pyproject without [tool.chitty]; pyproject with [tool.chitty] missing project; a comment mentioning archive; no contexts tables; a table between settings and contexts) fail before the fix

## Plan

Inspect init configuration discovery and upgrade rendering. Add failing filesystem-backed tests for standalone pyproject.toml, parsed missing settings, and table placement. Then make configuration ownership and insertion structure-aware, run make check, and verify each criterion.

## Notes

Ready for review: make check passes.

## Summary

Initialisation now ignores pyproject.toml files without [tool.chitty], derives missing settings from parsed TOML, and inserts them in the owning table before later tables. Verified with make check (131 tests).

## History

- 2026-10-27 → todo
- 2026-10-27 todo → doing
- 2026-10-27 doing → review
- 2026-10-27 review → done
