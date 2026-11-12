# Pipeline and feedback

Direction, not current behaviour. The human dropped the spec-first pilot
(TASK-109) on 2026-11-11; TASK-255 adds `planning` and `cold-read` statuses
instead.

```
backlog → design → tests → review-ticket → work → review-work → done
```

| stage           | who                 | leaves when                                                      |
|-----------------|---------------------|------------------------------------------------------------------|
| `design`        | human, strong model | the ticket meets the ready definition and passes a cold read     |
| `tests`         | fresh session       | spec tests are committed and fail for the expected reason        |
| `review-ticket` | human, for now      | the ticket is small and clear, and the tests match it            |
| `work`          | fresh session       | spec tests pass and are unchanged, and `make check` passes       |
| `review-work`   | fresh session       | the diff meets the ticket, judged without the worker's reasoning |

Each stage has a different session, and nobody reviews a stage they did. Any
number of workers and reviewers may run at the same time. `chitty run` takes
a per-ticket lock right after choosing its ticket and holds it until it
returns: an exclusive, non-blocking `flock` on `<git common dir>/chitty/run/<ID>.lock`,
shared by every worktree and never committed. The kernel releases it when the
process exits, so no lock goes stale. `next_action` skips locked tickets, a run
that loses the race chooses again, and `--ticket` refuses a locked ticket. A
committed claim was rejected because a killed run would leave it for a person
to clear; locks are machine-local because Chitty runs on one machine. The
sessions write the main checkout during setup and review merges; a Git
lock or dirty-file collision fails loudly, so rerun the affected session. A
failed review restarts in a fresh session with the finding added as a
criterion. The second failure stops for the human: by then the ticket is the
likely problem. Work and review-work block for a human if the design or tests
are wrong, and never edit the spec tests.

Scripted gates come first because they cost no tokens and cannot be talked
round. They never relax, since trust does not build up in agents: only the
human's sampling rate moves, and only on measured escapes.

Ready definition. A fresh agent can do the ticket and know when to stop, and
another can check the result without talking to the first:

- Criteria are executable: a test or command defines done.
- Scope is stated so a reviewer can reject on it, with an out-of-scope list.
- Decisions are made: no "use your judgement".
- It points at relevant files and patterns instead of pasting them.
- It lists every path or caller the behaviour must hold on.
- It does one thing. Aim for one to three criteria and a diff of a hundred or
  two lines. Five criteria or a few hundred lines is the limit, and reaching it
  is a prompt to split, not to carry on. `TASK-126`, at 16 criteria and about
  1,000 lines, failed six reviews.
- Criteria state behaviour and leave lists of cases to the tests, because a
  listed case can always be read more strictly.

Cold read: an implementing read has a fresh, cheap-model agent implement a code-
changing ticket in a detached worktree and run its tests with and without the
fix; when there is nothing to run, a stronger model reads the ticket and
referenced code instead. Decided with the human (2026-11-05): use a detached
worktree and keep the implementing commit under `refs/cold-read/<ID>/<n>`, not a
branch, because Chitty searches branches for ticket copies and history should
be retained after the worktree is removed. Workers and reviewers do not do it
(2026-11-04: a worker read the procedure in `AGENTS.md` as its own step), so the
procedure is printed for planners:

The planner's part lives in the planning role instructions printed by
`chitty guide plan`. The reader's part, its worktree, setup, cleanup and report
steps, is printed by `chitty guide cold-read <ID>`, so the planner starts a
reader with that output instead of writing the steps out each time. Keep a new
ticket in `backlog` until its cold read findings have outcomes, and only then
move it to `todo` (through `planning` and `cold-read` while it is written and
read), because `chitty run` picks up anything in `todo`: `TASK-147`
was claimed with a wrong fix while its cold read was still running.

Planning practice in this repository (from the human):

- Readers run on Haiku, to show what a weak model struggles with.
- Ticket text is concise: tight sentences, bullets, the current decision only.
  Git keeps the history.
- While a planner's own subagent reviews a ticket, the ticket keeps an owner,
  so `chitty run` leaves it alone.

Spec tests exercise a surface, never mocks of our own code. Code should have
several surfaces: the outer ones (CLI, MCP, HTTP, file format) and internal ones
such as a module, a pure function or an internal API (a facade, for example). A
surface the ticket names is part of its spec, so tests may call it directly. Property tests are the default, with a
one-line reason when none suits: a round trip for any parser or serialiser, and
a property over sequences of operations for any state machine. Spec tests are
written from the ticket, before and without sight of the implementation.

## Feedback loops

Agents do not learn from correction, so a lesson counts only once it changes
something read or run later. In order of preference, that is a mechanical
check, then a template, then a prompt rule. Prompt rules have a fixed budget:
adding one means removing one.

| loop         | sensor                                                  | changes                       |
|--------------|---------------------------------------------------------|-------------------------------|
| ticket       | cold-read mismatch; predicted versus changed files      | the ticket, before work       |
| failure      | each failure's cause, and whether it cited a criterion  | standing rules, or the ticket |
| escape       | later bugs linked to their source; sampled audits       | gates and sampling rate       |
| test strength | occasional mutation runs                               | survivors become tickets      |
| replay       | past work stages rerun against their spec tests         | prompt and model choices      |

A failure's cause is the earliest stage that should have caught it: `design`,
`tests`, `work`, `integration` (branch, merge, environment) or `review` (the
reviewer was wrong). Record it as `Review failed (<cause>): ...`. Every review
note, passing or failing, has one line per criterion below that first line:
`<number>: pass - <evidence>` or `<number>: fail - <reason>`. A test criterion
passes only with evidence that its test fails without the change. A later bug
gets the label `escape` and a note naming its source ticket.

A retro is a ticket, opened after every 10 `done` tickets. It proposes a few
changes, each naming the failure class it should reduce, and the human accepts
or rejects them. An audit samples 1 in 5 `done` tickets. Both frequencies are
starting points, limited by the human's time.

Agents never see these metrics. First-pass yield also rises if reviewers go
soft, so it is only read alongside escapes. Judge cost per accepted ticket,
including retries, not per run.
