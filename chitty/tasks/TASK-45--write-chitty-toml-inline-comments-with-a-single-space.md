---
title: Write chitty.toml inline comments with a single space
status: todo
created: 2026-10-28
---

## Description

init writes 'archive = "move"  # ...' with two spaces before the comment; taidy's TOML formatter turns it into one, so every new repo starts with a formatting diff. Fix the template and init's config upgrade, and make the commented autoformat example point at taidy so projects that run a formatter find the setting. Markdown escaping is out of scope: task fields are Markdown, and escaping '*' etc. would break deliberate emphasis, links and code. PLAN.md only promises that files parse to the same task after formatting, and projects with a formatter should set autoformat.

## Acceptance Criteria

- [ ] INITIAL_CONFIG and init's upgrade path write a single space before inline comments
- [ ] The commented example reads '# autoformat = "taidy format"  # run on every written task file', written with a single space
- [ ] A test runs the TOML formatter that taidy uses (or asserts the canonical text) on a freshly initialised chitty.toml and expects no change
- [ ] PLAN.md's config example matches the template

## Notes

Suggestion origin: circuitry

Decided with the human: no Markdown escaping of user text; circuitry should turn autoformat on (suggestion sent).

## History

- 2026-10-28 → backlog
- 2026-10-28 backlog → todo
