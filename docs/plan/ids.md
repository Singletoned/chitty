# IDs

`<PREFIX>-<n>`, e.g. `TASK-13`.

- `PREFIX` is the context's prefix: `[A-Z]+`, unique within a repo.
  Prefixes name queues (`TASK` for `tasks/`, `HUMAN` for `human/`), not
  projects or types: a ticket's project is the repo it lives in, and its
  type (bug, suggestion) can change while its ID must not, so type is a
  label. New repos always get `TASK`; existing custom prefixes keep working.
- `n` is a positive integer, unpadded: one above the highest number in
  committed ticket files on all local and remote-tracking branches, in the
  context's active or archive directory, plus uncommitted files in this
  checkout. Uncommitted tickets in other worktrees and unpushed work on other
  machines are not visible.
- A context with `random_ids = true` instead draws `n` at random from
  10000000 to 99999999, such as `BACKLOG-48213907`, retrying (a bounded number
  of times, then failing) when a number in that same visible set is taken.
  Random IDs let tickets raised on any branch avoid colliding, so only `main`
  hands out sequential numbers (decided 2026-11-05). The generated `backlog`
  context (`chitty/backlog/`, prefix `BACKLOG`) uses it; it is unrelated to the
  `backlog` status. Plain `chitty add` in a linked worktree targets this context
  so unrelated branch discoveries are filed for planning; explicit contexts
  still win, and inbox pulls use the default context.

Filename: `<ID>--<slug>.md`, or `<ID>.md` when the slug is empty. The slug
is derived from the title (lowercase, `[a-z0-9-]`, collapsed hyphens, max 60
chars; empty if the title has no ASCII alphanumerics) and follows it:
`edit --title` renames the file (`git mv` when tracked), and `chitty fix`
renames files whose slug has gone stale. It is there so `ls` is readable; the
ID is the identity, so renames never break references. Slugs never contain `--`, so the ID is everything before the
first `--`. The ID is not repeated in frontmatter.

Collisions: allocation counts committed ticket files on all local and
remote-tracking branches, in active and archive directories, so branches get
separate IDs. It does not see uncommitted tickets in other worktrees or
unpushed work on other machines; those can still collide. If a collision does
occur, `chitty check` reports the files involved; the human renames one and
fixes references by hand. Likewise, moving the highest-numbered task out of a
context lets its number be reused; accepted.

Referencing: commands accept `TASK-13`, or bare `13` for the default
context. Stored references (`depends_on`, `moved_from`) are always the full
`PREFIX-n` form; shorthand is expanded before writing.
