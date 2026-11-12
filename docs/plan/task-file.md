# Task file

```markdown
---
title: Add search to the task list
status: todo
labels:
  - search
  - cli
priority: medium
owner: ed
depends_on:
  - TASK-7
  - HUMAN-1
created: 2026-10-23
---

## Description

Free markdown.

## Acceptance Criteria

- [ ] `chitty list --search` matches title and body
- [x] Matching is case-insensitive

## Plan

Free markdown, written by the agent before implementing.

## Notes

Free markdown. Append-only by convention except `chitty edit --set-notes` and
`--set-notes-file`, which replace the section (`''` removes it). Replacement
cannot be combined with append-note options and is forbidden during review.

## History

- 2026-10-23 → todo
- 2026-10-28T14:03:05Z lively-otter todo → doing
```

## Frontmatter

Strict: unknown keys are an error.

| key          | type                | required | notes                                   |
| ------------ | ------------------- | -------- | --------------------------------------- |
| `title`      | string              | yes      | non-empty, one line                     |
| `status`     | see below           | yes      |                                         |
| `labels`     | list[string]        | no       | absent means `[]`                       |
| `priority`   | `low\|medium\|high` | no       | absent means unset                      |
| `owner`      | string              | no       | one line: `human`, a name, an agent     |
| `depends_on` | list[ID]            | no       | any context in the same repo            |
| `parent`     | ID                  | no       | groups tickets; same repo               |
| `created`    | date                | yes      | ISO 8601, set once                      |
| `moved_from` | ID                  | no       | set by `move`: the ID in the old context |

- Statuses: `backlog` (needs refining), `planning` and `cold-read` (being
  written), `todo`, `doing`, `blocked` (needs a reason), `review`, `done`.
- An owner reserves `todo` and `doing` tickets for that agent: see
  [Next action and runner](next-action-and-runner.md). `chitty run --ticket ID`
  ignores non-human owners.
- No `updated` field: Git has it, and the field would conflict on every merge.
- YAML scalars all load as strings, so `owner: no` is `"no"` and `status: on`
  is an unknown status, not `True`.
- Written free text (`title`, `owner`, `labels`) is quoted when YAML 1.1 or 1.2
  would read it as a non-string (`"no"`, `"2026-10-23"`, `"1e3"`). `created` is
  written unquoted.

## Body

- Sections are `##` headings: `Description`, `Acceptance Criteria`, `Plan`,
  `Notes`, `Summary`, `History`. Any other `##`, any `#`, or text before the
  first `##` is an error. Use `###` and below inside a section.
- Fence-aware: `##` in a code block is not a heading.
- `Description` is required and non-empty.
- `Acceptance Criteria` is a flat task list only. Items start `- [ ]`, `- [x]`
  or `- [X]` at column 0 and may continue on indented lines. Blank lines
  between items are allowed; anything else is an error. Items are numbered by
  position in the CLI, never in the text. The tool writes `- [x]`.
- Everything else is free Markdown.

## History

Tool-written, always last. Each deliberate change appends one line:

- create (`add`, `suggest`, inbox pull): `- <UTC time> actor → status`;
- status change, archive, restore: `- <UTC time> actor old → new`;
- any other edit that changes something: `- <UTC time> actor: action; action`,
  for example `changed priority, notes; wrote the plan; ticked acceptance
  criteria`. Review independence reads `wrote the plan` and `ticked
  acceptance criteria` from these;
- import: the source's creation line, which may be date-only, then
  `- <UTC time> actor: imported task`.

Not recorded: no-op edits, `chitty fix` repairs, reference rewrites in other
tickets, and `delete` (which removes the file). Date-only lines stay valid.

## Supported formatters

The round trip is tested, and claimed, only for:

- `prettier`, default settings and `proseWrap: always`;
- `mdformat` with `mdformat-gfm` and `mdformat-frontmatter` (plain mdformat
  turns `---` into a heading and escapes `[ ]`).

Notes:

- Both are pinned. If either is missing the tests fail; they never skip.
- "Survives" means the file parses to the same task. Byte-identical output is
  claimed only for ordinary content: `mdformat-frontmatter` writes YAML 1.2
  and drops the tool's 1.1 quotes, and mdformat renumbers ordered lists.

## Writing

A patch over the original text, never parse-then-dump:

- Frontmatter: one span per top-level key, with its indented lines and the
  comments and blank lines above it. Changed keys are replaced, new keys
  appended in table order, removed keys deleted. Every other byte stays.
- Body: one span per `##` section. Only changed sections are rewritten; new
  ones go in the order above.
- Criteria are patched per item, so wrapping survives: `--check`/`--uncheck`
  change the bracket, `--rm-ac` deletes the item, `--set-ac` replaces it in
  place unticked, `--ac` appends.
- Lists are written block style. Flow style is read and left alone unless that
  key changes.
- Unchanged content is not written.
- `--note TEXT` appends a paragraph to `## Notes`, creating it if needed.
  `--note-file F` reads it from a file (`-` for stdin). No date prefix.
- Criterion numbers in one `edit` refer to the list before it. `show` prints
  them.
