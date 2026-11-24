---
title: Let agents withdraw a suggestion they posted
status: backlog
created: 2026-11-24
---

## Description

An agent posted a suggestion with 'chitty suggest margay --create ...' and the user then chose a different approach in the same session. chitty has no command to withdraw or close a waiting suggestion (commands: add, archive, check, edit, fix, guide, import, inbox, init, list, mcp, move, next, note, path, pull, ...), so the agent had to delete ~/.local/share/chitty/inbox/margay/suggestion-<id>.md by hand. Suggest printing the suggestion id from 'chitty suggest' and adding 'chitty suggest --withdraw <id>' (or similar), so agents never edit the inbox directory directly.

## Notes

Suggestion origin: /Users/singletoned/src/efficio/margay-ornua

## History

- 2026-11-24T22:21:46Z zesty-coral-newt → backlog
- 2026-11-24T22:21:47Z zesty-coral-newt: changed notes
