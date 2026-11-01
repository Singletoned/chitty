---
title: Read Chitty's version from the code, not package metadata
status: done
priority: high
created: 2026-11-01
---

## Description

`CHITTY_VERSION` comes from `importlib.metadata`, which an editable install only refreshes on reinstall, so it reported 0.1.4 while running 0.1.5 code and `init` recorded the wrong `chitty_version` in other repos. Keep the version in one place the running code reads directly (for example `src/chitty/__init__.py` as the build's version source), so even an editable install reports correctly. `mate release` bumps that place.

## Plan

Move the canonical version into `src/chitty/__init__.py`; configure Hatchling to read that source for builds; update runtime loading and release documentation; add regression tests proving the running source wins over stale installed metadata. Run focused tests, `make check`, and commit the verified change.

## Notes

Blocked by `TASK-80`: release tooling must define the single source of truth it updates before version loading can change.

Unblocked (2026-11-01): TASK-80 is deferred, so this ticket chooses the single version source itself (for example `__version__` in `src/chitty/__init__.py`, read by the build), and the manual release process bumps it. Update the release steps in `AGENTS.md` to name that file.

Moved the canonical version to `src/chitty/__init__.py`; Hatchling builds and runtime configuration now read it directly. Verified focused regression, `make check`, and `make build`.

Reviewed: independent implementation in 49eb608 makes `src/chitty/__init__.py` the runtime and Hatch build version source. Verified `make check`, `make build`, and matching runtime/wheel metadata version `0.1.8`.

## History

- 2026-11-01 → backlog
- 2026-11-01 backlog → todo
- 2026-11-01 todo → blocked
- 2026-11-01 blocked → todo
- 2026-11-01 todo → doing
- 2026-11-01 doing → review
- 2026-11-01 review → done
