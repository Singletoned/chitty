---
title: Write chitty.toml inline comments with a single space
status: done
created: 2026-10-28
---

## Description

init writes 'archive = "move"  # ...' with two spaces before the comment; taidy's TOML formatter turns it into one, so every new repo starts with a formatting diff. Fix the template and init's config upgrade, and make the commented autoformat example point at taidy so projects that run a formatter find the setting. Markdown escaping is out of scope: task fields are Markdown, and escaping '*' etc. would break deliberate emphasis, links and code. PLAN.md only promises that files parse to the same task after formatting, and projects with a formatter should set autoformat.

## Acceptance Criteria

- [x] INITIAL_CONFIG and init's upgrade path write a single space before inline comments
- [x] The commented example reads '# autoformat = "taidy format"  # run on every written task file', written with a single space
- [x] A test runs the TOML formatter that taidy uses (or asserts the canonical text) on a freshly initialised chitty.toml and expects no change
- [x] PLAN.md's config example matches the template

## Plan

Inspect configuration template and init upgrade rendering, update both to canonical single-space TOML comments, add a focused initialization/formatting regression test, update PLAN.md, then run make format and make check.

## Notes

Suggestion origin: circuitry

Decided with the human: no Markdown escaping of user text; circuitry should turn autoformat on (suggestion sent).

Reviewed: the template and upgrade path use single-space comments. A freshly initialised `chitty.toml` is unchanged by `taidy format`, verified on a scratch repo. The tests assert the canonical lines and that no double-space comment appears.

## Summary

Updated generated configuration comments to the canonical single-space form, pointed the autoformat example at `taidy format`, and covered fresh initialization plus upgrade behavior. Verified with `make check`.

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
- 2026-10-28 todo → doing
- 2026-10-28 doing → review
- 2026-10-28 review → done
