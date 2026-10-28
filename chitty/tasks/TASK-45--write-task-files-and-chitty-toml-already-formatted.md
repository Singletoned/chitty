---
title: Write task files and chitty.toml already formatted
status: backlog
created: 2026-10-28
---

## Description

In circuitry, running the project formatter (taidy) after chitty commands changes chitty's output, so every chitty write leaves a formatting diff. Seen: (1) 'chitty add --ac "static/photos/*.jpg ..."' writes an unescaped '*' in a Markdown checklist item; the formatter rewrites it as '\*'. (2) The chitty.toml written by init has 'archive = "move"  # ...' with two spaces before the inline comment; the TOML formatter makes it one. Expected: chitty writes canonical Markdown/TOML (escape Markdown specials in user text, single-space inline comments), or runs the configured autoformat by default, so formatting is a no-op. The circuitry chitty.toml has '# autoformat = "mdformat"' commented out, which may be related.

## Notes

Suggestion origin: circuitry

## History

- 2026-10-28 → backlog
