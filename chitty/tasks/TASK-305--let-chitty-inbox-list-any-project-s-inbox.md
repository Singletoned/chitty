---
title: Let chitty inbox list any project's inbox
status: backlog
created: 2026-11-12
---

## Description

`chitty inbox` only works inside a Chitty repo: from a non-Chitty checkout it fails with "no chitty.toml or [tool.chitty] in pyproject.toml ... (run chitty init)". After `chitty suggest --create dotfiles ...` there was no way to check the suggestion had arrived except reading ~/.local/share/chitty/inbox/dotfiles/ by hand. An optional PROJECT argument (chitty inbox dotfiles) would allow that, and would let a human see suggestions waiting for projects that are not initialised yet.

Found 2026-11-12.

## Notes

Suggestion origin: /Users/singletoned/src/efficio/margay-eye-south

## History

- 2026-11-12T21:43:29Z kind-yellow-vole → backlog
- 2026-11-12T21:43:30Z kind-yellow-vole: changed notes
