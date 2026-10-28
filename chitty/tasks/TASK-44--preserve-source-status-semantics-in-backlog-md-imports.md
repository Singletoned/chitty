---
title: Preserve source-status semantics in backlog.md imports
status: backlog
created: 2026-10-28
---

## Description

Importing this repository emitted 'unknown status Backburner' for every Backburner task, fell back to Chitty's backlog status, and exited non-zero after creating the destination tasks. Because the non-zero exit stopped the importer before it deleted the otherwise clean tracked backlog/config.yml, users must repair cleanup manually. Map Backburner to backlog without an error (or make the mapping configurable) and complete clean-source removal when fallback is safe.

## Notes

Suggestion origin: circuitry

## History

- 2026-10-28 → backlog
