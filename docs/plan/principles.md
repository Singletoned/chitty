# Principles

- **Files are the truth.** No database, index or cache. A directory scan is
  fast enough for thousands of tickets.
- **One ticket, one file, one writer.** No locking or automatic conflict
  repair.
  - Two situations (the person, 2026-11-26). On `main`, Chitty gives the
    best view of the whole situation it can: it reads `main`'s copy and also
    any later versions on other branches, which may be several and may be
    stale (today only the ticket's own `task-<n>` branch, local or
    remote-tracking; TASK-603 and TASK-604 widen this). Off `main`, Chitty
    assumes it runs in isolation (perhaps later in a container with no other
    branches): it reads and writes the current branch's copy, warns about
    changes it can see elsewhere, and conflicts are resolved at merge time.
    Uncommitted files in the current worktree override committed state.
  - Writes warn rather than refuse ([Direction](direction.md)), with one
    exception: on `main`, an edit to a ticket whose `task-<n>` branch has a
    newer copy is refused, because writing `main`'s older copy would hide the
    work in progress. Writes never cross branches.
  - So worktrees need `autocommit = true` (or commit every Chitty write).
  - Sequential contexts allocate numbers on the configured main branch (or
    outside Git) and provisional IDs off it. `random_ids` contexts use random
    numbers on any branch. `check` reports duplicate IDs.
- **Simple first.** Add complexity when use shows the need.
- **Plain Markdown.** Every ticket file survives the supported formatters
  unchanged in meaning ([Task file](task-file.md)). No HTML comments, sentinel
  markers or numbers in checklist text.
- **External parsers, fixed data.** (Owner direction 2026-11-20, not yet
  built; `TASK-451` is to be replanned on it.) Read ticket files with
  external, well-tested parsers (`markdown-it-py` for Markdown, PyYAML for
  frontmatter) rather than hand-written line splitting and regexes, and cover
  the reader and writer with broad property tests. Fix the data before the
  calculations: once a file has been fixed (normalised), writing it back saves
  it byte for byte. Line-by-line editing is in doubt as the way to get there.
- **Loud errors.** A malformed file is rejected with a path and a reason, never
  silently repaired. `chitty check` is the compile step.
- **Chitty does the bookkeeping.** Whatever the tool can work out or keep
  consistent (derived status, references to finished tickets, dates, who did
  what), it does. Whatever a script can do reliably (branches, worktrees,
  setup, claiming, merging), `chitty run` does. Agents get only the judgement.
- **Chitty never calls a model.** Models sit only in the worker and reviewer
  seats. Which agent is configuration: agent-specific code stays in
  integrations.
- **The tool carries the rules.** Validation and `--help` document them; agent
  instructions stay short and static.
- **Minimal diffs.** Never touch a line that did not change; never write an
  unchanged file.
- **Projects and suggestions.** Each repository has a validated lower-case
  `project` name. `init` registers its machine-local inbox (XDG data) and
  refuses a name another repository owns. `suggest` writes an idea to another
  project's inbox; `inbox` lists them; `inbox --pull` imports them as backlog
  tickets.

## Setup and upgrades

- `chitty init` is idempotent: it adds missing setup, refreshes the managed
  `AGENTS.md` block, and migrates formats.
- It does not inspect or manage machine-wide Pi extensions or settings.
- Reads work with older setup; writes need it current. With
  `autocommit = true`, Chitty upgrades and commits setup separately before the
  write; otherwise it fails and says to run `chitty init`.
- Upgrades happen only in the main checkout. In a linked worktree a write
  skips the upgrade and the stale-setup error (but still refuses setup newer
  than Chitty); the branch gets the new setup when it merges `main`.
- `chitty run` refreshes setup before choosing a ticket: commits it in the main
  checkout, does nothing in a linked worktree. From a linked worktree it refuses
  when the main checkout's setup is older or unrecorded.
- A Chitty older than the recorded setup refuses writes.

## `chitty import backlog-md`

- One-way, from a Backlog.md `backlog/` directory. Never prompts.
- Refuses before writing unless the working tree is clean, untracked files
  included: Git history is the safety net.
- Duplicates are worse than deletion, so it `git rm`s each converted file in
  the import's commit. `--keep-source` keeps them.
- `backlog/config.yml` is consumed and removed under the same rules. Its
  declared statuses map to `backlog`, with one summary line each; only
  undeclared statuses are reported as unknown.
- Other non-ticket files stay and are reported. `backlog/` goes only if empty.
