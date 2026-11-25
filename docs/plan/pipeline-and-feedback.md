# Pipeline and feedback

## Flow

- `backlog` → `planning` → `cold-read` → `planning` → `todo` → `doing` →
  `review` → `done`; recoverable runner failures enter `error` and use an
  explicit repair run before returning to `review` or `blocked`.
- Planning, cold reading, work and review use different sessions; nobody reviews
  their own work.
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
  `doing` for a fresh worker session. Only genuine blockers return to
  `planning` (contradictions, false claims about the codebase, an unverifiable
  criterion, a consequential unresolved fork with competing alternatives, or a
  ticket too large for one session). External obstacles requiring help use
  `blocked`, with a short plain-English `Summary` for the human.
- A return to planning requires one nonblank note explaining the discoveries,
  why the ticket cannot guide the work, and the decisions or corrections needed,
  with evidence for each. Finish reading the ticket and inspecting relevant code
  before returning; keep the branch and worktree.
- Workers make decisions loudly: when a ticket leaves a small detail open, has
  a minor typo or miscount, or has one sensible default with no obvious
  competing alternative, the worker chooses it, records
  `Decided: <case> -> <choice>, because <reason>`, adds a focused test where
  useful, and keeps moving (widened 2026-11-25 after `echonomicon` `TASK-133`
  and `TASK-213` bounced repeatedly over minor omissions and prose typos).
  Reviewers accept sensible choices unless they violate requirements or cause a
  defect.
- Returned tickets appear in planning lists, not automatic work/review
  selection. The planner resumes in the existing ticket worktree, simplifies or
  revises the ticket, and follows the normal planning and cold-read steps before
  `todo`.
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
- Agents stop committing their own changes on `main` whenever a branch is
  easy (decided 2026-11-23, after a fix to a release script was committed
  straight to `main`). Each branch that starts from `main` and merges back is
  named by its kind: `task-<n>` for ticket work (made by the runner),
  `plan/<name>` for planning (recognised by `planning_branch`), and
  `hotfix/<name>` for a fix outside any ticket. Outside ticket work, the
  author does it in its own worktree, passes the configured checks, and then
  fast-forwards `main`; ticket branches still land only after review, as
  below. The managed guide block says so. Nothing treats `hotfix/` specially yet;
  Chitty's own ticket writes on `main` are `TASK-340`'s concern.

## Ready ticket

A fresh agent can do it and know when to stop; another can check it without
asking the first. And a human can read it quickly without wading through history.

- Criteria are executable: a test or command defines done.
- Scope is stated, with an out-of-scope list.
- Simple first, fail early: ground input contracts in the real source, reject
  bad input loudly at the boundary, and do not specify handling for speculative
  or cheap-to-fix edge cases.
- Points at files, patterns and every caller the behaviour must hold on,
  rather than pasting them.
- Does one thing: one to three criteria, a diff of a hundred or two lines. Five
  criteria or a few hundred lines is the limit; reaching it means split.
  (`TASK-126`, 16 criteria and about 1,000 lines, failed six reviews.)
- Criteria state behaviour and properties, leaving generator recipes and fixture
  wiring to the worker.
- Text is short and current: rewrite cleanly instead of appending caveats, and
  clear resolved notes (`--set-notes ''`) before `todo`. Git keeps the history.

## Cold read

- The planner's part is `chitty guide plan`; the reader's is
  `chitty guide cold-read <ID>`, which the planner passes to the reader.
- Every ticket gets a cold read (if a change is too small to justify a ticket
  and cold read, do it directly on a `hotfix/` branch instead). A fresh,
  cheap-model agent reads the ticket and the code and documents it names, with
  two equal jobs: find real blockers (what would make a reasonable worker build
  the wrong thing or write a weak test) and find ways to **simplify** (cut
  defensive bloat, narrow contracts, drop over-specified test mechanics). It
  makes no branch, ref or commit and leaves `git status` unchanged, but may
  write throwaway probes outside the checkout when faster than reading.
- The planner checks each claim about code, commands and tests against the
  source as it writes it, runs `chitty check` before starting a reader, and
  plans one ticket at a time. A criterion may mark tests that pin kept behaviour
  after `Regression tests:`, which must pass and need not fail without the
  change.
- **Dropped on 2026-11-25** (after `echonomicon` `TASK-133` grew to 2,080 words
  over 9 cold reads for 30 lines of code, and `TASK-213` bounced 4 times over
  prose edits):
  - Prose "wrong versions", pre-running generators during planning, and
    dictating generator recipes in ticket text. Reviewers check test strength
    directly for test-only changes, and mutation testing belongs in tools.
  - The separate sufficiency read (which duplicated the cold read with an
    adversarial bias toward defensive bloat).
  - Unbounded re-reading. Cold reads are capped at 1–2 rounds: one read is
    enough when it finds no real blockers; run a second only after substantive
    edits, and if a second read still finds serious problems, simplify, narrow,
    or split instead of patching again.
- Before `todo`, resolve findings by simplifying, narrowing, rejecting
  speculative edge cases, or fixing real blockers — preferring changes that make
  the ticket shorter. Clear stale notes before `todo`.
- Workers and reviewers never cold-read.
- A ticket reaches `todo` only after its findings have outcomes, because
  `chitty run` takes anything in `todo` (`TASK-147` was claimed mid-read).
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
  change, except a test the criterion marks as a regression test, which only has
  to pass.
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
