---
title: Have cold reads implement the ticket, and repeat them after changes
status: backlog
created: 2026-11-05
---

## Description

Evidence from planning about 15 tickets in `echonomicon` for a weaker model, using cheap fresh agents as cold readers. Suggest two additions to `chitty guide plan`.

1. A cold reader should implement the ticket in a disposable clone and run the tests its criteria describe, checking they fail without the fix, rather than only reading the ticket and the code. Read-only passes found wrong claims and missing details. Implementing found faults those passes had missed: a test that would have read the real user library, a test that passes with or without the fix, and a criterion that a wrong fix (`== 500` for `>= 400`) would still satisfy. It should be a real `git clone`, not `git archive`, as tools can behave differently without `.git`, and one reader reported a false failure that way.

2. Repeat the cold read after applying its findings, until the serious findings stop, as the fixes are a source of new faults. Sampling three fixed tickets at random for a second read found real problems in all three, two of them making `mate check` impossible to pass, so every fixed ticket was re-read. Those reads then found faults that the first-round fixes had introduced, such as a criterion left contradicting an updated description.

A related check to add: compare each decision in the description with the criteria, because implementers test what the criteria name. The first ticket done by the weaker model was correct, but left stated decisions untested, and auditing other tickets found the same gap. Also worth stating: an existing nearby test can pass without the fix, so a ticket should say which test must fail first.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-05T17:52:45Z mellow-newt → backlog
- 2026-11-05T17:52:46Z mellow-newt: changed notes
