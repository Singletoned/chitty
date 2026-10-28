---
title: Tests register throwaway projects in the real machine inbox
status: backlog
created: 2026-10-28
---

## Description

The real inbox at ~/.local/share/chitty/inbox/ contains projects registered to deleted temporary directories: fresh -> /private/var/folders/.../T/tmpykgifc3h/fresh, notes -> .../T/tmp639ta42c/notes and repo -> .../T/tmp1qrdl049/repo (all created 2026-10-27 15:56, matching tempfile.mkdtemp names, so most likely the test suite). circ points at an agent scratchpad from a chitty session. Real harm: the generic name 'repo' is now taken, and a genuine suggestion ('Repair Pi extension dependency links after npm install', origin ~/.pi, 2026-10-27) landed in inbox/repo/, where no real repository will ever pull it. Expected: tests point the inbox root at a temporary directory (an env var or fixture overriding inbox_path), and a test asserts the real inbox is untouched. Also consider: 'chitty suggest' warning or refusing when a registered project's repo path no longer exists, and a cleanup command or 'chitty fix' step that lists or prunes registrations whose paths are gone.

## Notes

Suggestion origin: circuitry

Needs refinement before implementation: make the required test inbox isolation outcome explicit, then decide whether stale-registration refusal and cleanup behavior belong here or in follow-up tickets. Add verifiable acceptance criteria for the chosen scope.

## History

- 2026-10-28 → backlog
