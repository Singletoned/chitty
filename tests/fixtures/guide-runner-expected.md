## Chitty

Tasks live in `chitty/`; use the `chitty` CLI or MCP, and do not hand-edit task files.
Put paths, commands, IDs, and code in backticks. When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`.
Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
Run `chitty --help` for the command reference.

A passing review lands through `chitty run`: it fast-forwards `main` only after
rebasing the ticket branch onto `main` and running the configured setup and
checks. Agents started without `chitty run` should first rebase the branch
onto `main` in its worktree and run the configured checks; after they pass, only
fast-forward `main`. Do not merge or remove branches or worktrees as a reviewer.

When starting an agent by hand, run the matching focused guide:

- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.

Workers may resolve a small omission when the ticket and existing code or tests
point to one clear, cheap-to-reverse default. It must preserve requirements
and acceptance criteria and introduce no new user-visible policy, command, or
setting. Record `Decided: <case> -> <choice>, because <reason>`, cite the
precedent, and add a focused test where testable. Reviewers check the choice,
precedent, and test against the same boundary. Do not invent or weaken a test
needed to verify a stated criterion.

Apart from that exception, workers and reviewers return a ticket to `planning`
for missing or contradictory requirements, an unresolved design decision, a
wrong claim about the code, files or other tickets, a criterion that cannot be
verified as written or would pass with nothing built, a test a criterion needs
that the ticket does not describe (its fixture, action and assertions), or a
ticket too large to finish in one session. Stop implementation, not
investigation, at the first planning blocker. Before changing status, finish
reading the ticket and checking relevant code and tests for the remaining
requirements. Report all actionable planning issues in one note with evidence
and the decision or correction needed. Say what could not be checked and why,
and continue with independent checks without speculating or expanding scope.
Preserve existing implementation work and follow normal
planning and cold-read readiness before resuming. Implementation defects against
clear requirements return to `doing`; external obstacles requiring help go to
`blocked`.

Every review note, whether passing or failing, has one line per criterion below
its `Reviewed:` or `Review failed (<cause>):` first line: `<number>: pass -
<evidence>` or `<number>: fail - <reason>`. Evidence is the command or test that
shows it. A test criterion passes only with evidence that the test fails without
the change.
