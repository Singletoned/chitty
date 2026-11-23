---
title: Allow per-repo custom statuses and priorities
status: backlog
created: 2026-11-23
---

## Description

Context: a personal todo repo (~/src/singletoned/todo) manages the user's life todos as one Markdown file per item with YAML frontmatter, the same model as Chitty. Assessed 2026-11-23 and not adopted; one reason is that Chitty's statuses and priorities are fixed and suit development work. docs/plan/non-goals.md lists "Configurable statuses" as a non-goal; the human has said (2026-11-23) to reconsider that, since Chitty is under our control.

What that repo needs:
- Statuses: open, waiting (blocked on someone or something external), done, dropped (decided not to do; distinct from done), and possibly someday. No planning, cold-read or review.
- Priorities as time horizons rather than low/medium/high: now (this week), soon (this month), later, someday. For life admin, "when" is more useful than "how important".

Proposal: let `chitty.toml` declare the vocabulary, for example
  statuses = ["open", "waiting", "done", "dropped"]
  priorities = ["now", "soon", "later", "someday"]   # in order, highest first
with the current values as the default, so existing repos are unchanged. `chitty check` validates against the configured lists. Priority order drives sorting in `list` and `next`.

Points to decide:
- The runner relies on specific statuses (todo, doing, review, done, blocked, planning, error). Simplest rule: custom statuses are only allowed with `workflow = "tickets"`; `workflow = "runner"` requires the built-in set (or a superset of it).
- Which configured statuses count as finished (for dependencies, archive and default `list` filtering), e.g. `closed_statuses = ["done", "dropped"]`.
- List glyphs and 5-letter abbreviations for custom statuses: derive them, or allow them in config.
- Update non-goals.md to match.

## Notes

Suggestion origin: /Users/singletoned/src/singletoned/todo

## History

- 2026-11-23T10:23:57Z witty-russet-gannet → backlog
- 2026-11-23T10:23:59Z witty-russet-gannet: changed notes
