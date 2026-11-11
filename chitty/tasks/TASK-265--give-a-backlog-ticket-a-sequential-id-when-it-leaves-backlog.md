---
title: Give a `BACKLOG-` ticket a sequential ID when it leaves `backlog`
status: backlog
depends_on:
  - TASK-264
parent: TASK-262
created: 2026-11-11
---

## Description

- Today a random-ID ticket must be promoted with `chitty move` (`store.py` refuses other statuses). Instead, in the main checkout, `chitty edit ID -s <status>` from `backlog` to anything else moves it to the default prefix with the next number, rewriting references and setting `moved_from`, as `chitty move` does.
- Outside the main checkout, refuse with a message saying to promote from the main checkout.

## History

- 2026-11-11T11:35:14Z vivid-yellowhammer → backlog
