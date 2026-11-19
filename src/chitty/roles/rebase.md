A rebase onto the integration branch stopped on conflicts. Resolve each
conflicted file, keeping the intent of both sides, then stage it with `git add`.
Run `git -c core.editor=true rebase --continue` (the continuation command is
`git rebase --continue`) and repeat until no rebase is in progress. Never run `git rebase --abort` or `git rebase --skip`.

After the rebase finishes, run the configured setup and check commands, and fix
anything the rebase broke.
