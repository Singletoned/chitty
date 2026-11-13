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
- `--summary` writes the optional final handoff section, after Notes.
- `parent` is a full ticket ID for grouping; shorthand IDs are expanded. It must
  exist and cannot form a cycle. `list --parent ID` shows direct children;
  `show` lists them.

## `list`

- Non-archived tickets only. Default statuses: `planning`, `cold-read`,
  `todo`, `doing`, `blocked`, `review`, from every context. `-c` and `-s`
  narrow and repeat; `-s` can add `backlog` and `done`. `--all` is every
  status, still without archives.
- Order: selected statuses, then `high`, `medium` or unset, `low`. `--json`
  uses the same order.
- Rows: `TASK-12  🔨 doing  ⬆️  Add search to the task list  [cli,search]`.
  - Status glyphs: `💤 bklog`, `📝 plan`, `🔎 cold`, `📋 todo`, `🔨 doing`,
    `⛔ blckd`, `👀 revw`, `✅ done`.
  - Priority column only when a listed ticket has one: `⬆️` high, `⏺️`
    medium, `⬇️` low, blank unset.
  - Skip column, only when needed: `👤` human, `🔒` waiting, `▶` running, `⚠️`
    broken (message on stderr).
  - Titles are cut with `…` to fit `list_width`, counting emoji as two
    columns; labels stay whole. No branch.
- JSON keeps status words and adds `skipped`: `👤 human`,
  `🔒 waits on ID[, ID...]`, or `⚠️ <message>`.
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
- `move ID CTX`: within this repository; next number in the target, same
  slug, sets `moved_from`. No cross-repository move: `suggest` there, then
  `archive` here.
- `renumber PATH` repairs two files sharing an ID, as a merge of two branches
  can leave. Such files collapse into one ticket for `show`, `edit` and
  `list`, so it takes a path. It refuses a path that is not a ticket in a
  context, or whose ID no other file uses (`move` covers that).
  - The file keeps its slug, gets the next number, and records `moved_from`.
  - References are never rewritten: a `depends_on` or `parent` naming a shared
    ID cannot say which file it meant. It lists every ticket naming the old ID
    for a person to check.
