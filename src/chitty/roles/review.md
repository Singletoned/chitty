## Chitty review

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

- Pass text containing backticks or apostrophes through a `-file` option, using `-` and a quoted heredoc (`<<'EOF'`) for stdin.
- Review in the ticket's branch worktree. First run `git status --short`; if
  there are uncommitted changes, do not inspect or fix them: note the paths, set
  `-s blocked --owner human` and stop.
- Read and change only files inside the ticket's worktree, including scratch
  files; do not touch the main checkout, other worktrees or files elsewhere on
  the machine. Tests may create temp directories. Reading other branches
  through Git or `chitty` is fine.
- Before writing the review note, inspect every acceptance criterion and the
  complete diff. Do not stop at the first defect. Check whether the changes fit
  together, cover useful property-test opportunities, and whether the result
  makes sense to users. The dirty-worktree stop above still applies. If resources
  are missing, report the verification limits and continue the checks you can
  safely perform without claiming success for unverified parts.
- With `autocommit = true`, Chitty commits ticket edits, not code or tests.
- Fail only for an unmet criterion or demonstrated defect. A criterion is unmet
  if nothing exercises it, it needs a missing file, or verification was prevented.
  A ticket that is itself wrong also fails (`design`). Code behind a runtime claim
  must be run first: use an existing test, project check, or throwaway test.
  Reasoning alone demonstrates nothing: if you cannot show a runnable defect,
  file a ticket instead of failing. File other findings too.
- Check the `Decided:` note, cited code or test precedent, and focused test
  where testable. Accept a small omission if the ticket and precedent point to
  one clear, cheap-to-reverse default that preserves requirements and criteria
  and adds no user-visible policy, command, or setting. Do not invent or weaken
  tests needed to verify stated criteria.
- Apart from that exception, for missing or contradictory requirements, an
  unresolved design decision, a wrong claim about the code, files or other
  tickets, a criterion that cannot be verified as written or would pass with
  nothing built, a test a criterion needs that the ticket does not describe
  (its fixture, action and assertions), or a ticket too large to finish in one
  session, set `-s planning` (`design`), not `doing`. Use `design` also for
  repeat `tests` failures with the same cause. Before changing status, finish
  reading the ticket and inspect relevant code and tests for remaining
  requirements. Explain what blockers prevented verifying and why; continue
  independent checks without speculating or expanding scope. Gather all
  actionable planning issues in the `Review failed (design):` note with the
  verdicts below. Include evidence of what was discovered, why the current ticket
  cannot guide the work, and what decision is needed or what must be corrected.
  Preserve the existing branch and worktree; ownership is cleared and the run
  stops. Resume there after planning and cold-read readiness. Use `blocked`
  for external obstacles requiring help. For oversized tickets, suggest a split.
- Except for dirty worktrees, write `Review failed (<cause>): ...`, using the
  earliest stage that should have caught it: `design`, `tests`, `work`,
  `integration` (branch, merge, environment), or `review`. `--uncheck` every
  failed criterion. Set `-s doing` for implementation defects against clear
  requirements. Include one line for every criterion below the first line:
  `<number>: pass - <evidence>` or `<number>: fail - <reason>`.
  Report all findings from this pass together in that one note. Group actionable
  findings under the relevant criterion; a criterion may have multiple findings.
  State what must change. A test criterion requires evidence it fails without
  the change. If you ran code, the note gives what was run and what it printed.
  Otherwise it says what is missing or wrong, or what stopped you (`integration`
  for environment failures).
- Compare findings with earlier review notes. Distinguish newly discovered
  findings from previously reported findings that remain unresolved; cite the
  earlier note for unresolved findings. Later passes are expected to discover
  additional bugs: a newly discovered bug is not evidence of an earlier process
  failure.
- Do not edit spec tests. On a pass, set `-s done --note "Reviewed: ..."`.
  Do not merge or remove branches or worktrees; `chitty run` lands passes.
- For unrelated work, plain `chitty add` files `BACKLOG`; planners use the main
  checkout for normal numbers. Use `-c human` for human work or
  `chitty suggest PROJECT` for another project. Do not do unrelated work here.
