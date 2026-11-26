# CLI

`chitty --help` and `chitty <command> --help` are the command reference. This
file holds the decisions behind them.

## General

- `--json` on reads, and on writes (printing the resulting ticket).
- Every error exits non-zero with a message on stderr.
- No prompts or wizards; flags specify everything.
- Shell completion (Click's, bash and zsh) completes ticket IDs and contexts
  inside a repository, and nothing outside one.
- IDs: `TASK-13` in any case, or bare `13` for the default context. Output and
  writes use upper case. `check` reports lower-case `depends_on` entries; `fix`
  rewrites them.
- `-c/--context` defaults to `default_context` and names a context in this
  repository. Other repositories get work through `chitty suggest`;
  `contexts.toml` is ignored with a warning.

## `add` and `edit`

- `-d` is required, except with `-s backlog`, which writes
  `This ticket needs refining.`
- Notes: append with `--note`/`--note-file`, or replace with
  `--set-notes`/`--set-notes-file` (empty removes the section). Replacing
  cannot be combined with appending and is refused in review.
- Description: `--description-file` is available on `add`, `edit` and `suggest`.
- `--plan-file` and `--summary-file` are available on `edit`; `--summary`
  writes the optional final handoff section, after Notes.
- File options read UTF-8 and accept `-` for stdin; their text-option twins
  also accept a bare `-` for stdin. Only one option may use stdin.
- `parent` is a full ticket ID for grouping; shorthand IDs are expanded. It must
  exist and cannot form a cycle. `list --parent ID` shows direct children;
  `show` lists them.

## `list`

- Non-archived tickets only. Default statuses: `planning`, `cold-read`,
  `todo`, `doing`, `blocked`, `error`, `review`, from every context. `-c` and `-s`
  narrow and repeat; `-s` can add `backlog` and `done`. `--all` is every
  status, still without archives.
- Order: selected statuses, then tickets labelled `bug`, then `high`, `medium`
  or unset, `low`. `--json` uses the same order.
  - 2026-11-25: tickets labelled `bug` sort first within each status.
- Rows: `TASK-12  🔨 doing  ⏫  Add search to the task list  [cli,search]`.
  - Status glyphs: `💤 bklog`, `📥 plan`, `📝 plnng`, `🔎 cold`, `📋 todo`, `🔨 doing`,
    `⛔ blckd`, `💥 error`, `👀 revw`, `✅ done`.
  - Priority column only when a listed ticket has one: `⏫` high, `➖`
    medium, `⏬` low, blank unset.
  - Skip column, only when needed: `👤` human or owned, `🙋` untestable,
    `🔗` waiting, `🏃` running, `💔` broken (message on stderr), or `🚧` for an
    active ticket with waiting dependents and no unfinished or broken dependency
    of its own. Every unfinished ticket that is not running, human or owned shows
    `🔗` or `💔` for its dependencies, whatever its status; running, human,
    owner and dependency markers come before `🚧`. `🚧` considers dependents across
    all active tickets, even when the list is filtered.
  - Titles are cut with `…` to fit the smaller of `list_width` and the terminal width when stdout is a terminal, counting emoji as two
    columns; labels stay whole. No branch.
- JSON keeps status words and adds `skipped`: `👤 human` or owned,
  `🙋 untestable`, `🔗 waits on ID[, ID...]`, or `💔 <message>`.
- An empty result reports its filters on stderr; stdout (JSON too) stays empty.

## `check` and `fix`

- `check` is read-only. Errors exit non-zero; warnings do not.
- `fix` applies safe repairs, reports what remains, and exits non-zero only
  for remaining errors. It never rewrites warning-only Markdown: use backticks
  for literal delimiters in code.
- Autocommit runs `fix` on written files first; only errors block it.

## `archive`, `move`, `renumber`

- `archive` with no ID processes every non-archived `done` ticket in one
  batch; run it before a merge request.
  - `archive = "move"` (default): move into `archive/`, History
    `… → archived`.
  - `archive = "delete"`: delete the file and its History, remove exact
    `depends_on` entries elsewhere; numbers stay used, read from Git.
- `move ID CTX`: within this repository; allocates a new ID in the target
  context, keeps the slug, sets `moved_from`, and rewrites `depends_on` and
  `parent` references. No cross-repository move: `suggest` there, then
  `archive` here.
- `renumber` without a path renumbers provisional tickets on main. It prints
  `renumbered <old ID> -> <new ID> <path>` on stdout for each ticket. If there
  is nothing to renumber, it prints `nothing to renumber` on stderr; off main,
  it prints `provisional tickets are renumbered on main; nothing changed` on
  stderr. Both cases exit 0. With `--json`, stdout is a list of renumbered
  tickets, empty when nothing changes.
- `renumber PATH` repairs two files sharing an ID, as a merge of two branches
  can leave. Such files collapse into one ticket for `show`, `edit` and
  `list`, so it takes a path. It refuses a path that is not a ticket in a
  context, or whose ID no other file uses (`move` covers that).
  - The file keeps its slug, gets a new ID by the context's allocation rules,
    and records `moved_from`.
  - References are never rewritten: a `depends_on` or `parent` naming a shared
    ID cannot say which file it meant. It lists every ticket naming the old ID
    for a person to check.
- Both commands allocate IDs like `add`: random numeric IDs in `random_ids`
  contexts, sequential numbers on the configured main branch or outside
  Git, and provisional IDs marked `provisional: true` otherwise.
