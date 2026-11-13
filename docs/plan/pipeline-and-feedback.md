# Pipeline and feedback

## Flow

- `backlog` → `planning` → `cold-read` → `planning` → `todo` → `doing` →
  `review` → `done`; recoverable runner failures enter `error` and use an
  explicit repair run before returning to `review` or `blocked`.
- A different session does each step; nobody reviews their own work.
- Scripted gates come first: they cost no tokens and cannot be argued with.
  They never relax. Only the human's sampling rate moves, and only on measured
  escapes.
- The third failed review since the ticket was last `blocked` blocks it for
  the human (`REVIEW_FAILURE_LIMIT`): by then the ticket is the likely problem.
- A failed review restarts in a fresh session, with the finding added as a
  criterion (TASK-307 lets reviewers fail on an uncovered requirement).
- Workers and reviewers block for the human when the ticket is wrong. They
  never weaken its tests.
- The earlier spec-first pipeline (separate `design`, `tests` and
  `review-ticket` stages, TASK-109) was dropped on 2026-11-11; git has it.

## Concurrency

- Any number of workers and reviewers may run at once.
- `chitty run` holds an exclusive, non-blocking `flock` on
  `<git common dir>/chitty/run/<ID>.lock` from choosing a ticket until it
  returns. Never committed; the kernel frees it on exit, so it never goes
  stale.
- `next_action` skips locked tickets; a run that loses the race picks again;
  `--ticket` refuses a locked ticket.
- Locks are machine-local: Chitty runs on one machine.
- Sessions write the main checkout during setup and merges. A Git lock or
  dirty-file collision fails loudly; rerun that session.

## Ready ticket

A fresh agent can do it and know when to stop; another can check it without
asking the first.

- Criteria are executable: a test or command defines done.
- Scope is stated, with an out-of-scope list.
- Decisions are made: no "use your judgement".
- Points at files, patterns and every caller the behaviour must hold on,
  rather than pasting them.
- Does one thing: one to three criteria, a diff of a hundred or two lines. Five
  criteria or a few hundred lines is the limit; reaching it means split.
  (`TASK-126`, 16 criteria and about 1,000 lines, failed six reviews.)
- Criteria state behaviour and leave cases to the tests, because a listed case
  can always be read more strictly.
- Text is concise: bullets, the current decision only. Git keeps the history.

## Cold read

- The planner's part is `chitty guide plan`; the reader's is
  `chitty guide cold-read <ID>`, which the planner passes to the reader.
- Code-changing ticket: a fresh, cheap-model agent implements it in a detached
  worktree and runs its tests with and without the fix. Otherwise a stronger
  model reads the ticket and the code it names.
- The implementing commit is kept under `refs/cold-read/<ID>/<n>`, not a
  branch, because Chitty reads tickets from every branch.
- Workers and reviewers never cold-read.
- A ticket reaches `todo` only after its findings have outcomes, because
  `chitty run` takes anything in `todo` (`TASK-147` was claimed mid-read).
- In this repository readers run on Haiku, to show what a weak model struggles
  with. While a planner's own subagent works on a ticket, the ticket keeps an
  owner, so `chitty run` leaves it alone.

## Spec tests

- Test a surface, never mocks of our own code.
- Code should have several surfaces: outer ones (CLI, MCP, HTTP, file format)
  and internal ones (a module, a pure function, an internal API such as a
  facade). A surface the ticket names is part of its spec, so tests may call
  it directly.
- Property tests are the default, with a one-line reason when none suits: a
  round trip for a parser or serialiser, a property over sequences of
  operations for a state machine.
- Written from the ticket, before and without sight of the implementation.

## Review notes

- First line `Reviewed: ...` or `Review failed (<cause>): ...`. The cause is the
  earliest step that should have caught it: `design`, `tests`, `work`,
  `integration` (branch, merge, environment) or `review`.
- Then one line per criterion: `<number>: pass - <evidence>` or
  `<number>: fail - <reason>`.
- A test criterion passes only with evidence that the test fails without the
  change.
- A later bug gets label `escape` and a note naming its source ticket.

## Feedback loops

- Agents do not learn from correction, so a lesson counts only when it changes
  something read or run later. Prefer a mechanical check, then a template, then
  a prompt rule. Prompt rules have a fixed budget: adding one means removing
  one.

| loop          | sensor                                                 | changes                       |
| ------------- | ------------------------------------------------------ | ----------------------------- |
| ticket        | cold-read mismatch; predicted versus changed files     | the ticket, before work       |
| failure       | each failure's cause, and whether it cited a criterion | standing rules, or the ticket |
| escape        | later bugs linked to their source; sampled audits      | gates and sampling rate       |
| test strength | occasional mutation runs                               | survivors become tickets      |
| replay        | past work rerun against its spec tests                 | prompt and model choices      |

- A retro ticket every 10 `done` tickets proposes a few changes, each naming
  the failure class it should reduce; the human accepts or rejects. It also
  checks `docs/plan/` against the code, fixes stale facts, and drops decisions
  that use has overturned. An audit
  samples 1 in 5 `done` tickets. Both rates are starting points.
- Agents never see these metrics. First-pass yield also rises when reviewers go
  soft, so read it only alongside escapes. Judge cost per accepted ticket,
  retries included.
