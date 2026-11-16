# Direction

Stated by the human on 2026-11-10:

- Chitty's original purpose is a plain, tickets-only task tracker. The runner
  pipeline (worktrees, review, landing and role guides) is an optional layer
  selected by repository workflow.
- Short term, in order: stabilise, have agents write property tests, then run
  agents in containers.
- Long term: run both locally with worktrees and in a forge's runner pool.
  Tickets stay files in git; the forge is only a remote and a runner pool.
- So design changes to work from a fresh clone that pushes to a remote, as
  well as from a local worktree. `../pithos/` has tried the container side.

Stated by the human on 2026-11-16:

- Once agents run in containers, one loop starts an agent for whatever ticket
  is next, in whichever mode it needs: work, review, or repair of an `error`
  ticket. Until then, `chitty run --errors` stays a separate, explicit run, so
  do not add error repair to the normal loop as a stopgap.
- Containers also replace guide rules about where agents may read and write
  (for example "keep scratch files inside the worktree"): the sandbox
  enforces it, and the rule can be removed from the guides.
