# IDs

- `<PREFIX>-<n>`, such as `TASK-13`. The ID is not repeated in frontmatter.
- `PREFIX` is the context's prefix: `[A-Z]+`, unique in the repository. It
  names a queue (`TASK` for `tasks/`, `HUMAN` for `human/`), not a project or
  type: a ticket's type can change but its ID cannot, so type is a label. New
  repositories get `TASK`; custom prefixes keep working.
- `n` is unpadded: one above the highest number in the ticket files of the
  main checkout with the current prefix, active or archived, committed or not (with
  `archive = "delete"`, also numbers deleted on any branch). Only `main`
  hands out sequential numbers; elsewhere new tickets get provisional IDs.
- `random_ids = true` draws `n` from 10000000 to 99999999 instead
  (`BACKLOG-48213907`), retrying up to `RANDOM_ID_ATTEMPTS` times. Random IDs
  avoid the numbers in this checkout's files only; a clash with another branch
  is possible but unlikely and accepted.
- The `backlog` context (`chitty/backlog/`, prefix `BACKLOG`) uses random IDs.
  It is unrelated to the `backlog` status. Plain `chitty add` in a linked
  worktree files there; an explicit `-c` wins, and inbox pulls use the default
  context.

## Filenames

- `<ID>--<slug>.md`, or `<ID>.md` when the slug is empty.
- The slug comes from the title: lower case, `[a-z0-9-]`, hyphens collapsed, at
  most 60 characters, empty without ASCII letters or digits. It never contains
  `--`, so the ID is everything before the first `--`.
- `edit --title` renames the file (`git mv` when tracked); `chitty fix` renames
  stale slugs. The slug only makes `ls` readable, so renames break nothing.

## Collisions

- Uncommitted tickets in other worktrees and unpushed work elsewhere are not
  visible, so they can collide. `chitty check` reports the files;
  `chitty renumber PATH` gives one the next number ([CLI](cli.md)).
- Moving the highest-numbered ticket out of a context lets its number be
  reused; accepted.

## References

- Commands take `TASK-13` or bare `13` for the default context.
- Stored references (`depends_on`, `parent`, `moved_from`) are always full
  `PREFIX-n`.
