---
title: Make suggest --create work with a path
status: backlog
created: 2026-11-12
---

## Description

`chitty suggest --create ~/.dotfiles "title"` fails with "Error: no Chitty configuration in /Users/singletoned/.dotfiles". In inbox.py suggest(), a PROJECT containing / is treated as a path and must already have Chitty config, so --create is ignored; --create only works with a bare name, which then registers the project with no path. Either let --create with a path register that path under its directory name (so a later `chitty init` there finds the inbox), or reject --create with a path and say to pass a name. The help says only "Create an inbox for a non-Chitty project", which suggests a path should work.

Found 2026-11-12 while posting a suggestion to ~/.dotfiles from a Margay session.

## Notes

Suggestion origin: /Users/singletoned/src/efficio/margay-eye-south

## History

- 2026-11-12T21:43:28Z kind-yellow-vole → backlog
- 2026-11-12T21:43:29Z kind-yellow-vole: changed notes
