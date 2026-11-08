---
title: Stop `chitty init` writing a double blank line before `<!-- chitty:end -->`
status: backlog
created: 2026-11-06
---

## Description

The block that `chitty init` (0.1.34) manages in `AGENTS.md` ends with two blank lines before `<!-- chitty:end -->`. Markdown formatters such as `taidy` (via `mdformat` or `prettier`) collapse them to one, so every `make format` after a `chitty init` dirties `AGENTS.md`, and the next `chitty init` puts the line back. Emit one blank line. This is related to the suggestion about formatting task files on every write: Chitty-written Markdown should already be in formatter-stable form.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-06T16:25:28Z youthful-vole → backlog
- 2026-11-06T16:25:29Z youthful-vole: changed notes
