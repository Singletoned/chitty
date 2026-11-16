A passing review lands through `chitty run`: it fast-forwards `main` only after
merging `main` into the ticket branch and running the configured setup and
checks. Agents started without `chitty run` should first merge `main` into the
branch in its worktree and run the configured checks; after they pass, only
fast-forward `main`. Do not merge or remove branches or worktrees as a reviewer.

When starting an agent by hand, run the matching focused guide:

- `chitty guide work` for implementation.
- `chitty guide review` for review.
- `chitty guide plan` for writing or refining tickets.

Workers and reviewers return a ticket to `planning` for missing or contradictory
requirements, an unresolved design decision, a wrong claim about the code, files
or other tickets, a criterion that cannot be verified as written or would pass
with nothing built, or a ticket too large to finish in one session. The note
explains the discovery, why the ticket cannot guide the work, and the decision
needed. Preserve existing implementation work and follow normal planning and
cold-read readiness before resuming. Implementation defects against clear
requirements return to `doing`; external obstacles requiring help go to
`blocked`.

Every review note, whether passing or failing, has one line per criterion below
its `Reviewed:` or `Review failed (<cause>):` first line: `<number>: pass -
<evidence>` or `<number>: fail - <reason>`. Evidence is the command or test that
shows it. A test criterion passes only with evidence that the test fails without
the change.
