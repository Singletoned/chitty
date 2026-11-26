A ticket lands on `main` only after its review passes; a worker never lands
its own ticket. Under `chitty run`, the runner lands it: it rebases the ticket
branch onto `main`, runs the configured setup and checks, then fast-forwards
`main`. Reviewers there do not merge or remove branches or worktrees. A reviewer
started by hand whose review passed rebases the branch onto `main` in its
worktree, runs the configured checks and, once they pass, only fast-forwards
`main`.

When starting an agent by hand, run the matching focused guide:

- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.

A ticket that cannot guide the work goes back to `to-plan` with a note giving
the evidence and the decision needed; external obstacles go to `blocked`,
implementation defects to `doing`.

Every review note, passing or failing, starts `Reviewed:` or `Review failed
(<cause>):`, then has one line per criterion: `<number>: pass - <evidence>` or
`<number>: fail - <reason>`, where evidence is the command or test that shows
it. A test criterion passes only with evidence that the test fails without the
change, except a test the criterion marks as a regression test, which only has
to pass.
