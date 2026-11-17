# Repair

You are repairing an automated Chitty run that ended in `error`.

- Read the ticket's Notes and inspect the preserved branch and worktree, if they exist, before changing code.
- If the ticket branch was missing, search reflogs, other worktrees, and `git log --all` for commits whose `Task:` trailer is exactly this ID and that change files other than the ticket file. If found, reset the branch to that commit, note its ID and the evidence, then set the ticket to `review`. If none is found, set it to `blocked` and say what was searched.
- Resolve the reported failure, not unrelated work. Keep the ticket's acceptance criteria and scope.
- Commit code and task changes in the ticket worktree.
- If repaired, set the ticket to `review`; do not review it yourself.
- If a human or external decision is required, set the ticket to `blocked` with a concise note explaining what is needed.
- Do not leave the ticket in `error`, `todo`, or `doing` when you finish.
