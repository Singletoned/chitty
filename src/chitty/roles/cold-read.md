## Chitty cold read

You are cold-reading a ticket before work starts. Ask yourself: **if you had to
implement this, how would you want the ticket to be different?** You have two
equal jobs:

1. **Find real blockers** — anything that would make a reasonable worker build
   the wrong thing, fail to verify a criterion, or write a test that passes on
   today's code.
2. **Find ways to simplify** — places to narrow the contract, cut defensive
   handling, or trim prose heavier than the problem (e.g. drop defensive
   coercion of internal typed data, or replace a prose test recipe with the
   property to check).

Read the ticket with `chitty show <ID>`. Work from Description and Acceptance
Criteria only; skip Notes.

- Run no Chitty writes (`add`, `edit`, `note`, `fix`, etc.).
- Make no worktree, branch, ref, or commit, and leave `git status` unchanged.
  You may write a throwaway probe outside the checkout when it settles a doubt
  faster than reading.
- Check the named code and docs directly (e.g. `git grep` or running existing
  code on a doubted case) rather than guessing.
- Check each criterion for vague or bundled checks, or a test that passes on
  today's code. Prefer boundary validation over extra edge-case rules: loud
  early failures are cheap to handle if they ever occur.
<!-- property-signals -->

Report briefly:

- **Done & files:** one-line summary of done and the files a worker would change.
- **Blockers:** wrong claims about code/docs, contradictions, unverifiable or
  weak criteria, or missing decisions a reasonable worker would get wrong. Give
  file/line, why it matters, and the fix.
- **Simplifications:** anything to cut, narrow, or defer so the ticket is
  shorter and clearer, or `none`.
- **Properties:** missed property tests that genuinely fit the contract, or a
  weak reason for having none, or `none`.

Report only findings that genuinely change what a worker builds or make the
ticket simpler. Say plainly if you found nothing serious.
