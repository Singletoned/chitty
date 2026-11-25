---
title: "Workers: decide small, clear choices instead of returning to planning"
status: backlog
created: 2026-11-25
provisional: true
---

## Description

Evidence (echonomicon, 2026-11-24): TASK-213 went back to planning because it said "five temporary edits" but listed four, plus a separately described historic checkout. The intent was obvious. Earlier it bounced after saying "four wrong versions, only three given" while its own note listed four. TASK-133 went back to planning over how to treat non-string values in text columns. That needed one `isinstance` check, and the real data has none. Each bounce costs a full planning, cold-read and worker cycle. A wrong decision costs one review comment.

`chitty guide work` currently allows a default only for a "small omission" with "one clear default". It sends "contradictions, unclear or consequential choices" to planning. Weak workers read a typo or a miscount as a contradiction.

Suggestion: widen the omission exception. A worker decides when the ticket's intent or the code points to one answer, even if the text is inconsistent. It records `Decided: <case> -> <choice>, because <reason>` and lets review push back. A return to planning has to name a concrete case where any plausible choice could fail review. Optionally, have the runner reject a planning return whose note does not name that case.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-25T22:28:17Z calm-ochre-quail → backlog
- 2026-11-25T22:28:18Z calm-ochre-quail: changed notes
