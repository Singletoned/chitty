---
title: "Case study: specification runaway on echonomicon TASK-133 (30 lines of code, 2,000 words of spec, 13 sessions, nothing committed)"
status: backlog
created: 2026-11-25
provisional: true
---

## Description

A worked example of the planning–work loop growing a ticket far beyond the
size of its problem, without converging. Written 2026-11-25 for Chitty, as an
example of what the process must prevent. All figures come from the
echonomicon repository's git history and `chitty show TASK-133`.

### The problem being solved

Echonomicon reserves a short key for every live podcast, with the shortest
keys going to the most popular. Step one turns the Podcast Index SQLite dump
(4.77M rows in its `podcasts` table) into a ranked list of live podcasts:

- keep rows that are not dead, have HTTP status 200, at least one episode, a
  non-blank title and URL, and an item within 365 days of the newest item in
  the dump;
- sort by popularity, then episode count, then id.

That is a filter and a sort: roughly 30 lines of Python, or one SQL
`WHERE … ORDER BY`. The design doc already described it in a paragraph.

### What happened

| When (2026) | Event | Description size |
|---|---|---|
| 11-12 20:12 | Ticket written | 390 words |
| 11-24 12:25 | Unparked; `author` and `artwork_url` added | 462 |
| 11-24 15:21–15:32 | Cold reads 2–6: each finding answered with new rules, examples and tests | 530 → 921 → 1,161 (peak) → 1,122 |
| 11-24 15:37 | Worker 1 takes it, writes a plan, returns it to planning after 2 minutes: "too large to complete in this session" | — |
| 11-24 ~22:00 | Split: example tests to TASK-BCHE6A (579 words), malformed-column tests to TASK-VY5XWK (399 words) | ~1,100 |
| 11-24 22:20–22:25 | Cold reads 7–9: generator recipe refined (near-miss rows, U+2028, time shifts) | ~1,100 |
| 11-24 22:28 | Worker 2: runner check error on a stale uncommitted draft; ticket to `error` | — |
| 11-24 22:51 | Triage back to `doing` with instructions | — |
| 11-24 22:53 | Worker 3 returns it to planning: what to do with a non-null, non-string value in `podcastGuid`, `itunesAuthor`, `imageUrl`? | 1,098 |

The totals at the time of writing:

- Specification: about 2,080 words across three tickets, for about 30 lines
  of code.
- Notes on TASK-133: 1,114 words, mostly cold-read findings and their fixes.
- Sessions: 9 cold reads, 3 worker sessions, plus 3 planning sessions and a
  triage. None of them committed any code. The only code is an uncommitted
  draft in the worktree with type errors.

#### What the specification ended up containing

- An integer-reading helper, `_int_column`, specified to accept `int`, `bool`
  and digit strings, and to raise a named `ValueError` for anything else.
  Each of seven columns gets a `ValueError` example.
- Duplicate-id detection "after conversion", so that `7` and `"7"` collide.
- A Hypothesis strategy specified in prose, in detail:
  - three row kinds (live, near-miss, mixed) in roughly equal shares;
  - a maximum timestamp drawn from 1971 to 2100, assigned to a non-live row
    at least half the time;
  - titles and URLs including `"\t\n"` and U+2028;
  - digit-string variants of every integer column;
  - a time shift of up to `10**9` seconds, written back as strings.
- A reference implementation in the test, which must not call the module.
- Thirteen "wrong versions" of the code, spread over three tickets, with the
  test that kills each one.

#### The ground truth, checked afterwards

HUMAN-4 (downloading the dump) finished on the evening of 11-24. On 11-25,
`SELECT typeof(col), count(*) … GROUP BY 1` over all 4,768,189 rows found:

- `itunesAuthor`, `imageUrl`, `podcastGuid`: `text` in every row.
- `popularityScore`, `dead`: `integer` in every row.
- No nulls, and no mixed types.

Almost all the type-defence rules, and the question that sent the ticket back
to planning the second time, guard against values that do not exist in the
only data source the function will ever read.

### Why it happened

These causes compound, and each one is reasonable on its own.

1. **The contract was set before anyone looked at the data.** The input was
   declared `Mapping[str, object]` while the dump was still a placeholder
   ("TASK-230 checks these names against the real dump"). An `object` input
   type makes every column's every type a legitimate question.

2. **Every finding was resolved by adding text.** `chitty guide plan` says:
   resolve every reader finding by strengthening, splitting or rejecting.
   Strengthening is the path of least resistance, and nothing asks "can this
   case occur?" The "open inputs" and "parsers and validators" property
   signals push further towards defending against everything.

3. **A cold read always finds something.** The reader's brief is to find what
   the ticket gets wrong. The guide re-triggers a read after any fix that
   changes what the worker builds. So reads only stop when one happens to
   report nothing serious. Reads 4–9 each found something, and each fix
   invited another read. The brake ("split after a third read with serious
   problems") fired once, late, and splitting kept all the text.

4. **The planner was writing the tests.** The guide asks planners to specify
   generators, run them against wrong versions while planning, and record the
   results. That moves test design into prose, where it is long, brittle and
   hard for a weak worker to follow. Cold read 9 then had to build the
   strategy to check the prose. That is the work itself, done during planning
   and then thrown away.

5. **Longer tickets give workers more places to stop.** Worker 1 judged the
   ticket too large. Worker 3 found an unspecified case: non-strings in text
   columns. That case exists only because the contract was `object`, and only
   because the ticket was detailed enough to make its absence look like a
   gap. Each bounce led to more specification.

6. **No one owned the question "is this proportionate?"** Each session saw
   only its own step: a reader checked completeness, a worker checked
   executability, a planner resolved findings. None was asked, or had the
   context, to notice that 2,000 words and 13 sessions had gone into
   30 lines.

### The same pattern elsewhere, from the same night

- **TASK-213** (a property test for feed generation) went from doing to
  planning four times, always over the prose describing its "wrong versions":
  - a count mismatch ("four wrong versions" with three given);
  - prose edits a worker could not apply;
  - a wrong expected exception (`FileNotFoundError` vs an assertion), repeated
    by a planning answer that had not checked the code;
  - finally, "five temporary edits" when four were listed.
  Never over the feature.
- **TASK-217** (S3 subscription records) is the counterexample: its bounces
  found real defects, namely deleted regression tests, a fake S3 that refused
  plain overwrites, and a fixture that cannot pass without
  `ECHONOMICON_FEED_BASE_URL`. The loop is not always waste. The waste comes
  when findings are about hypothetical inputs or ticket wording.

### What would have stopped it

In order of how early they act:

1. **Ground the contract in the source.** The design said the input is the
   dump. Planning should have waited for HUMAN-4, or taken the schema from
   Podcast Index's published SQL. With typed columns, the conversion helper, its
   `ValueError` examples, the digit-string generators, the "after conversion"
   duplicate rule and TASK-VY5XWK all disappear. Rule: when a real source exists, the contract comes from it,
   and one boundary check rejects anything else. Write no behaviour for
   inputs outside the contract.
2. **A proportionality check at every transition.** A cheap model (for
   example Jev, already used in echonomicon for review at about $0.04 per
   million tokens) is asked at every status change: given the problem
   statement, the ticket size, the session count and the last note, is this
   proportionate, or has it got stupid? It needs the whole history, which no
   step-level agent sees.
3. **Deterministic tripwires in `chitty check`:**
   - description length relative to criteria (TASK-133 had 2 criteria and
     1,100 words, so the existing 5-criterion warning never fired);
   - more than 3 cold reads;
   - more than 2 worker returns to planning.
   Each one escalates to the owner or a stronger planner instead of another
   cheap round.
4. **Mutation testing as a tool, not prose.** Replace hand-written "wrong
   versions" with a configured mutation run at review. That deletes the
   largest and most brittle part of both TASK-133 and TASK-213.
5. **Let workers decide when intent is clear.** "Five" vs four, and what to
   do with a non-string author, are worker decisions. Record a `Decided:` note
   and let review object. A bounce has to name a case where any reasonable
   choice could fail review.

### The underlying lesson

Separating planning from work is not the flaw. The flaw is that the loop
between them has gain greater than one: each pass adds more specification
than it resolves. Nothing in the loop measures the total, and no participant
is asked to. Human teams damp the same loop through a person who sees the
whole thing and is accountable for the outcome, through cost that people feel,
and through workers trusted to use judgement. Chitty needs explicit
equivalents of all three.

## Notes

Suggestion origin: echonomicon

## History

- 2026-11-25T22:28:22Z calm-ochre-quail → backlog
- 2026-11-25T22:28:23Z calm-ochre-quail: changed notes
