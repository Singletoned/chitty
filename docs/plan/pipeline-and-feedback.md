# Pipeline and feedback

## Flow

- `backlog` → `planning` → `cold-read` → `planning` → `todo` → `doing` →
  `review` → `done`; recoverable runner failures enter `error` and use an
  explicit repair run before returning to `review` or `blocked`.
- Planning, cold reading, work and review use different sessions; nobody reviews
  their own work. The sufficiency read is part of planning: the original planner
  evaluates the independent cold read, rather than starting another session.
- Tickets that can't be tested get the label and owner `untestable`
  (decided 2026-11-16), and skip the cold read, work and review: a human has
  a strong agent do them. Wording in guides, docs and prompts, and content
  writing, are the usual case: quicker to make than to specify, and review only
  checks them against their criteria (`TASK-336`, a guide rewrite, passed review
  while deleting unrelated advice).
- Scripted gates come first: they cost no tokens and cannot be argued with.
  They never relax. Only the human's sampling rate moves, and only on measured
  escapes.
- The third `review → doing` failure since the ticket was last `blocked` blocks
  it for the human (`REVIEW_FAILURE_LIMIT`), to investigate the repeated failures.
- A failed review of implementation against clear requirements returns to
  `doing` for a fresh worker session. Apart from the small-omission exception
  below, missing or contradictory requirements, an unresolved design decision,
  a wrong claim about the code, files or other tickets, a criterion that cannot
  be verified as written or would pass with nothing built, an unspecified test
  needed to verify a stated criterion, or a ticket too large to finish in one
  session returns to `planning`, from either `doing` or `review`. External
  obstacles requiring help use `blocked` instead.
- A return to planning requires one nonblank note explaining the discoveries,
  why the ticket cannot guide the work, and the
  decisions or corrections needed, with evidence for each. The first blocker
  stops implementation, not investigation: before returning to `planning`,
  finish reading the ticket and inspecting relevant code and tests. Report what
  could not be checked and why; continue checking independent requirements
  without speculating or expanding scope. Reviewers retain independence and
  one verdict per criterion, with at least one fail when criteria exist.
  Ownership is cleared; existing implementation, branch and worktree are
  preserved. The run ends without landing or starting another worker.
- A worker can resolve a small omission when the ticket and existing code or
  tests point to one clear, cheap-to-reverse default. The choice must preserve
  stated requirements and acceptance criteria and introduce no new user-visible
  policy, command, or setting. Note `Decided: <case> -> <choice>, because <reason>`,
  cite the precedent, and add a focused edge-case test where testable. Reviewers
  check the choice, precedent, and test against that same boundary rather than
  returning the ticket to planning just because it omitted the case. Neither
  role invents or weakens a test needed to verify a stated criterion.
- Returned tickets appear in planning lists, not automatic work/review
  selection. The planner resumes in the existing ticket worktree, revises or
  splits the requirements, and follows the normal planning and cold-read
  readiness steps before `todo`. The existing escalation counts only
  `review → doing` failures. Repeated-cycle diagnosis is separate work across
  the whole project pipeline: requirements, implementation, verification, review
  or workflow may be responsible; repeated failures do not prove planning failed.
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
- Every ticket gets a cold read. A fresh, cheap-model agent reads the ticket
  and the code and documents it names, and reports ambiguities and decisions.
  Its key question: are the tests the ticket asks for good, failing on today's
  code and on a plausible wrong implementation? It makes no branch, ref or
  commit and leaves `git status` unchanged, but may write throwaway files
  outside the checkout, such as a probe test, when that settles a doubt
  (decided 2026-11-18, loosening the read-only rule of 2026-11-16). Finding
  problems, not building, is its purpose.
- The planner checks each claim about code, commands and tests against the
  source as it writes it, runs `chitty check` before starting a reader, and
  plans one ticket at a time (2026-11-18). When the tested code already
  exists, the ticket lists wrong versions for the worker to commit as tests
  that assert each one fails (2026-11-20: hand runs recorded in notes were
  skipped by workers twice on `TASK-471`; move checks from agents to
  automation where safe), the planner runs each generator recipe against the real code before
  the read, and distractor values are built from the drawn value. Property
  tests are the exception (2026-11-23, from echonomicon, where 5 of 11 planned
  wrong versions passed naive generators): the planner runs the generators
  against each wrong version while planning and fixes any that let one pass,
  and the worker re-runs them once against each wrong version and records the
  result in a note. Committed hand-written wrong versions add clutter and drift.
- These habits worked on their first use (2026-11-19, `TASK-370`, `TASK-373`,
  `TASK-377`, `TASK-403`, `TASK-404`): checking a claim at the source showed a
  revert was safe; the third-read split caught a claim written without
  checking; asking whether the tests are good found unforced tie cases,
  distractors equal to the ticket branch, and a criterion failing on `main`
  for the wrong reason; a probe of about 20,000 cases per recipe agreed with
  the implementation.
- The original planning session then performs the sufficiency read on the
  ticket text, named code and documents, and reader report. For each criterion
  and the ticket as a whole, ask whether a plausible minimal implementation
  could meet the criteria but still reasonably fail a good review.
- Each gap needs a concrete counterexample, relevant varying inputs or state,
  distinguishing verification and observable result, and proposed criterion
  wording. Prefer general properties to accumulating examples; challenge
  coverage of the agreed problem, not speculative features.
- Before `todo`, resolve reader findings and sufficiency gaps by strengthening
  or splitting the ticket, or explicitly rejecting findings as out of scope.
  Write missing requirements into the ticket, not just the conversation. A
  problem the read misses follows the expected route back to planning. A
  stronger reader is optional for uncertainty or repeated work–review failures,
  not mandatory.
- Workers and reviewers never cold-read.
- A ticket reaches `todo` only after its findings have outcomes, because
  `chitty run` takes anything in `todo` (`TASK-147` was claimed mid-read).
- Rounds: the ticket-state migration (2026-11-18, 29 tickets) took about 2.5
  reads per ticket, two to four on most strong fixes and 13 across `TASK-378`
  and its splits. Later rounds mostly found errors the fixes had introduced (a
  command that does not exist, a wrong test base class, a spy on a function
  the code calls legitimately), not misses by earlier readers. So check every
  new claim about code, commands or tests against the source before rereading,
  and split a ticket whose third read still finds problems rather than patching
  it again.
- Read-only reads (from 2026-11-16) cost about a third less each than the
  earlier reads that wrote probe tests (Haiku, 79 reads against 78: about 12
  turns each against 26), and still found design flaws. More rounds per ticket
  used up the saving: cost per ticket stayed about the same.
- In this repository readers run on Haiku, to show what a weak model struggles
  with. Planners in Claude Code start the `cold-reader` agent
  (`.claude/agents/cold-reader.md`) with only the ticket ID: it fetches
  `chitty guide cold-read <ID>` itself, so the guide is never pasted by hand
  (2026-11-19, after a pasted `$(...)` reached a reader unexpanded). While a planner's own subagent works on a ticket, the ticket keeps an
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

- Inspect every acceptance criterion and the complete diff before writing the
  note; do not stop at the first defect. Check coherence, useful property-test
  opportunities, and whether the result makes sense to users. A dirty worktree
  still stops review immediately. Missing resources limit verification: report
  the limits and continue the checks that can safely run, without passing
  unverified parts.
- Report all findings from the pass together in one note. Group actionable
  findings under the relevant criterion, allowing multiple findings per
  criterion, each stating what must change. Existing failure rules still apply:
  fail for unmet criteria or demonstrated defects, not unrelated improvements.
- Distinguish newly discovered findings from previously reported findings that
  remain unresolved, citing the earlier note for unresolved findings. Later
  passes are expected to discover additional bugs; a new discovery is not
  evidence of an earlier process failure.
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
