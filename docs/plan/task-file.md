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

`History` is tool-managed, always last, and records every deliberate change:

- Creation by `add`, `suggest` or inbox pull writes
  `- YYYY-MM-DDTHH:MM:SSZ actor → status`, with a UTC timestamp and the
  creating actor.
- An import keeps the source's creation entry, which may be the legacy
  date-only `- YYYY-MM-DD → status` form, and appends
  `- YYYY-MM-DDTHH:MM:SSZ actor: imported task`.
- A status change, archive or restore appends
  `- YYYY-MM-DDTHH:MM:SSZ actor old → new`.
- An `edit` that changes anything other than status appends one event,
  `- YYYY-MM-DDTHH:MM:SSZ actor: action; action`, naming what changed, for
  example `changed priority, notes; wrote the plan; ticked acceptance
  criteria`. Review independence reads `wrote the plan` and `ticked acceptance
  criteria` from these events. An `edit` that changes nothing writes nothing.

Not recorded: rewriting references in other tasks after a move, rename or
delete, `chitty fix` repairs, and `delete`, which removes the task and its
History. Existing date-only entries remain valid.

Frontmatter schema (strict: unknown keys are an error):

| key          | type               | required | notes                                        |
|--------------|--------------------|----------|----------------------------------------------|
| `title`      | string             | yes      | non-empty, single line                       |
| `status`     | `backlog\|planning\|cold-read\|todo\|doing\|blocked\|review\|done` | yes     | fixed in v1; backlog needs refinement; planning and cold-read are ticket-writing states; blocked needs a reason |
| `labels`     | list[string]       | no       | absent ≡ `[]`                                |
| `priority`   | `low\|medium\|high` | no      | absent means unset                           |
| `owner`      | string             | no       | free text; `human`, a name, an agent         |
| `depends_on` | list[ID]           | no       | any context in the same repo                 |
| `created`    | date               | yes      | ISO 8601 date, set once                      |
| `moved_from` | ID                 | no       | set by `move`; the ID in the source context  |

An owner reserves work tickets for that agent. Plain `chitty next` and
`chitty run` select unowned `todo`/`doing` tickets, but still select owned
`review` tickets unless the owner is `human`; `--owner NAME` selects only that
agent's tickets in any active status. Empty and `human` owner filters are
refused. Explicit `chitty run --ticket ID` ignores non-human ownership.

There is no `updated` field. Git records when a file changed; the field would
add a line to every diff and conflict on every merge.

YAML is loaded with every scalar as a string (no implicit typing), so
`owner: no` is the string `"no"` and `status: on` fails validation as an
unknown status rather than becoming `True`. Pydantic parses `created` from
the string. When the tool *writes* a free-text field (`title`, `owner`,
`labels`) it quotes anything YAML 1.1 or 1.2 would read as a non-string
(`"no"`, `"2026-10-23"`, `"1e3"`), because other tools reading the file
won't be as careful. `created` is a real date and is written unquoted.

Body rules:

- Sections are `##` headings. Recognised: `Description`, `Acceptance
  Criteria`, `Plan`, `Notes`, `Summary`, `History`. `History` is last and
  contains only tool-written status entries. Unrecognised `##` headings, any `#` heading,
  and non-blank content before the first `##` are errors. Use `###` and below
  inside a section for structure.
- The parser is fence-aware: `##` inside a fenced code block is not a heading.
- `Description` is required and non-empty.
- `Acceptance Criteria` contains only a flat task list. An item starts with
  `- [ ]`, `- [x]` or `- [X]` at column 0 and may continue on following
  indented lines (formatters wrap long items). Blank lines between items are
  allowed. Nested lists, unindented prose, and anything else in the section
  are errors. Each item is one criterion, addressed by 1-based position in
  the CLI; no numbers are stored in the text. The tool writes `- [x]`.
- Everything else is free markdown.

## Supported formatters

The round-trip guarantee is tested against, and only claimed for:

- `prettier` with default settings, and with `proseWrap: always`;
- `mdformat` with the `mdformat-gfm` and `mdformat-frontmatter` plugins
  (plain CommonMark mdformat turns `---` into a heading and escapes `[ ]`).

Both are pinned to exact versions. If either is missing, the round-trip
tests fail loudly; they are never skipped.

"Survives" means the file still parses to the same task. Byte-for-byte
no-op is only claimed for ordinary content: `mdformat-frontmatter`
re-serialises YAML as 1.2 and drops the quotes the tool adds for 1.1
readers (`"no"` becomes `no`), and mdformat renumbers ordered lists in free
markdown.

## Writing

Serialisation is a patch over the original text, not parse-then-dump:

- Frontmatter is split into one span per top-level key (the key's line plus
  any indented lines under it). Changed keys have their span replaced, new
  keys are appended in table order, removed keys have their span deleted.
  Every other byte — comments, quoting, blank lines — is left alone.
  Comment and blank lines belong to the key below them, so replacing a key
  keeps the comment above it.
- The body is split the same way, one span per `##` section. Only sections
  the command changed are rewritten; new sections are appended in the
  canonical order above.
- Acceptance Criteria are patched per item, so formatter wrapping survives:
  `--check`/`--uncheck` change only the bracket character, `--rm-ac`
  deletes that item's lines, `--ac` appends one line.
- Lists are written block-style (one item per line). Flow style is accepted
  on read and left alone if the key isn't being changed.
- If the resulting content equals the current content, the file is not
  written.
- `--note TEXT` appends `TEXT` as a new paragraph (preceded by a blank line)
  to `## Notes`, creating the section if absent. `--note-file F` reads one note
  from a file (`-` for stdin). No date prefix; include one in the text if you
  want it.
- Creating a task writes an actor-attributed UTC initial History transition.
  A changed `--status`, archiving, and restoring append a transition; a no-op
  status edit does not. Every other `edit` that changes the task appends one
  actor-attributed event naming the changed fields, notes, plan or criteria.
  Imports retain their source creation entry and append an import event; safe
  `fix` repairs, `delete`, and reference rewrites in other tasks append none.
- All checklist indices in a single `edit` refer to the list as it was
  before the command ran. `show` prints the numbers next to each criterion so
  callers don't count.
