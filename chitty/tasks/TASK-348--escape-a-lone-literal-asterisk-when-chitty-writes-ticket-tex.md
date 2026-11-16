---
title: Escape a lone literal asterisk when Chitty writes ticket text
status: backlog
created: 2026-11-16
---

## Description

Every guide tells agents to escape a single literal `*` or wrap it in backticks, because Markdown formatting would otherwise change it. Have Chitty escape a lone `*` outside code spans when it writes descriptions, criteria and notes, so the instruction can go. Planning checks how the formatter round-trip treats it.

## History

- 2026-11-16T09:59:59Z intrepid-coral-raven → backlog
