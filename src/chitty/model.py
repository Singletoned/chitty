"""Parse, validate and patch a single task file.

Serialisation is a patch over the original text: the file is split into
spans (one per top-level frontmatter key, one per `##` section, one per
acceptance criterion) and only the spans an edit touches are rewritten.
Every edit re-parses its own output, so an edit can never produce a file
that `parse` would reject.
"""

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date
from itertools import combinations
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from chitty.errors import ChittyError
from chitty.ids import ID_RE

STATUSES = ("todo", "doing", "done")
PRIORITIES = ("low", "medium", "high")
FIELD_ORDER = (
    "title",
    "status",
    "labels",
    "priority",
    "owner",
    "depends_on",
    "created",
    "moved_from",
)
DESCRIPTION = "Description"
ACCEPTANCE_CRITERIA = "Acceptance Criteria"
PLAN = "Plan"
NOTES = "Notes"
SECTION_ORDER = (DESCRIPTION, ACCEPTANCE_CRITERIA, PLAN, NOTES)

DELIMITER = "---\n"
KEY_LINE_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)[ \t]*:(?:[ \t]|$)")
HEADING_RE = re.compile(r"( {0,3})(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
FENCE_OPEN_RE = re.compile(r" {0,3}(`{3,}|~{3,})")
CRITERION_RE = re.compile(r"- \[([ xX])\](?:[ \t]+(.*?))?[ \t]*$")
LIST_MARKER_RE = re.compile(r"(?:[-*+]|[0-9]+[.)])(?:[ \t]|$)")
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
BRACKET_COLUMN = 3

# Plain scalars that a YAML 1.2 (core schema) or YAML 1.1 reader would type as
# something other than a string. PyYAML's emitter covers most of 1.1 already.
YAML_TYPED_RE = re.compile(
    r"""(?x)
    ~ | null | Null | NULL
    | true | True | TRUE | false | False | FALSE
    | y | Y | n | N | yes | Yes | YES | no | No | NO | on | On | ON | off | Off | OFF
    | [-+]?[0-9][0-9_]*
    | 0o[0-7]+ | 0x[0-9a-fA-F]+ | 0b[01]+
    | [-+]?(?:\.[0-9]+|[0-9][0-9_]*(?:\.[0-9_]*)?)(?:[eE][-+]?[0-9]+)?
    | [-+]?\.(?:inf|Inf|INF) | \.(?:nan|NaN|NAN)
    | [0-9]{4}-[0-9]{1,2}-[0-9]{1,2}.*
    """
)


class TaskError(ChittyError):
    """A task file, or an edit to one, is invalid."""


class _StringLoader(yaml.SafeLoader):
    """Resolves every plain scalar as a string: `no` is "no", not False."""


_StringLoader.yaml_implicit_resolvers = {}


def _check_single_line(value: str) -> str:
    if not value.strip():
        raise ValueError("must not be empty")
    if "\n" in value:
        raise ValueError("must be a single line")
    return value


def _check_id(value: str) -> str:
    if not ID_RE.fullmatch(value):
        raise ValueError(f"{value!r} is not a task ID (PREFIX-N, e.g. TASK-13)")
    return value


class Frontmatter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str
    status: Literal["todo", "doing", "done"]
    labels: list[str] = []
    priority: Literal["low", "medium", "high"] | None = None
    owner: str | None = None
    depends_on: list[str] = []
    created: date
    moved_from: str | None = None

    @field_validator("title", "owner")
    @classmethod
    def _single_line(cls, value: str | None) -> str | None:
        return None if value is None else _check_single_line(value)

    @field_validator("labels")
    @classmethod
    def _labels(cls, value: list[str]) -> list[str]:
        for label in value:
            _check_single_line(label)
        if len(set(value)) != len(value):
            raise ValueError("contains duplicates")
        return value

    @field_validator("depends_on")
    @classmethod
    def _depends_on(cls, value: list[str]) -> list[str]:
        for item in value:
            _check_id(item)
        if len(set(value)) != len(value):
            raise ValueError("contains duplicates")
        return value

    @field_validator("moved_from")
    @classmethod
    def _moved_from(cls, value: str | None) -> str | None:
        return None if value is None else _check_id(value)

    @field_validator("created", mode="before")
    @classmethod
    def _created(cls, value: object) -> object:
        if isinstance(value, str) and not DATE_RE.fullmatch(value):
            raise ValueError(f"{value!r} is not an ISO 8601 date (YYYY-MM-DD)")
        return value


@dataclass(frozen=True)
class Criterion:
    checked: bool
    text: str
    start: int  # line offsets within the section, heading at 0
    end: int


@dataclass(frozen=True)
class _FieldSpan:
    key: str | None  # None for anything before the first key
    leading: tuple[str, ...]  # comments and blank lines directly above the key
    lines: tuple[str, ...]


@dataclass(frozen=True)
class _Section:
    name: str
    lines: tuple[str, ...]  # heading first


FieldValue = str | list[str] | date | None


@dataclass(frozen=True)
class Task:
    frontmatter: Frontmatter
    _fields: tuple[_FieldSpan, ...]
    _preamble: tuple[str, ...]
    _sections: tuple[_Section, ...]
    criteria: tuple[Criterion, ...]

    # -- reading ---------------------------------------------------------

    def render(self) -> str:
        parts = [DELIMITER]
        parts += [line for span in self._fields for line in (*span.leading, *span.lines)]
        parts.append(DELIMITER)
        parts += self._preamble
        parts += [line for section in self._sections for line in section.lines]
        return "".join(parts)

    def section(self, name: str) -> str | None:
        """The section's content without its heading, or None if absent."""
        for section in self._sections:
            if section.name == name:
                return "".join(section.lines[1:]).strip("\n")
        return None

    def as_dict(self) -> dict[str, Any]:
        data = self.frontmatter.model_dump(mode="json")
        data["description"] = self.section(DESCRIPTION)
        data["acceptance_criteria"] = [
            {"index": index, "checked": c.checked, "text": c.text}
            for index, c in enumerate(self.criteria, start=1)
        ]
        data["plan"] = self.section(PLAN)
        data["notes"] = self.section(NOTES)
        return data

    # -- editing ---------------------------------------------------------

    def with_field(self, key: str, value: FieldValue) -> "Task":
        """Set a frontmatter key; None or [] removes it."""
        if key not in FIELD_ORDER:
            raise TaskError(f"unknown frontmatter key {key!r}")
        fields = list(self._fields)
        index = next((i for i, s in enumerate(fields) if s.key == key), None)
        if value is None or value == []:
            if index is not None:
                del fields[index]
        else:
            lines = tuple(_render_field(key, value))
            if index is not None:
                fields[index] = replace(fields[index], lines=lines)
            else:
                fields.insert(_insert_position(fields, key), _FieldSpan(key, (), lines))
        return self._rebuild(fields=fields)

    def with_section(self, name: str, text: str) -> "Task":
        """Replace a section's content; empty text removes the section."""
        if name == ACCEPTANCE_CRITERIA:
            raise TaskError("acceptance criteria are edited per item")
        lines = _text_lines(text)
        sections = list(self._sections)
        index = self._section_index(name)
        if not lines:
            if index is not None:
                del sections[index]
                _strip_trailing_blank(sections)
            return self._rebuild(sections=sections)
        if index is None:
            return self._insert_section(name, lines)
        is_last = index == len(sections) - 1
        heading = sections[index].lines[0]
        sections[index] = _Section(name, (heading, "\n", *lines, *([] if is_last else ["\n"])))
        return self._rebuild(sections=sections)

    def with_note(self, text: str) -> "Task":
        """Append a paragraph to Notes, creating the section if absent."""
        lines = _text_lines(text)
        if not lines:
            raise TaskError("note must not be empty")
        index = self._section_index(NOTES)
        if index is None or self.section(NOTES) == "":
            return self.with_section(NOTES, text)
        sections = list(self._sections)
        old = list(sections[index].lines)
        last = max(i for i, line in enumerate(old) if line.strip())
        sections[index] = _Section(NOTES, (*old[: last + 1], "\n", *lines, *old[last + 1 :]))
        return self._rebuild(sections=sections)

    def with_criteria(
        self,
        add: Sequence[str],
        remove: Sequence[int],
        check: Sequence[int],
        uncheck: Sequence[int],
    ) -> "Task":
        """Edit acceptance criteria. Indices are 1-based, against the current list."""
        count = len(self.criteria)
        named = {"--rm-ac": remove, "--check": check, "--uncheck": uncheck}
        for flag, indices in named.items():
            for index in indices:
                if not 1 <= index <= count:
                    raise TaskError(f"{flag} {index}: there are {count} acceptance criteria")
        for a, b in combinations(named, 2):
            both = sorted(set(named[a]) & set(named[b]))
            if both:
                raise TaskError(f"criterion {both[0]} is given to both {a} and {b}")
        new_lines = [f"- [ ] {_criterion_text(text)}\n" for text in add]
        if not (remove or check or uncheck or new_lines):
            return self
        index = self._section_index(ACCEPTANCE_CRITERIA)
        if index is None or not self.criteria:
            if not new_lines:
                return self
            return self._insert_section(ACCEPTANCE_CRITERIA, new_lines, replace_existing=True)
        lines = list(self._sections[index].lines)
        items = self.criteria
        kept: list[list[str]] = []
        for number, item in enumerate(items, start=1):
            if number in remove:
                continue
            own = lines[item.start : item.end]
            if number in check or number in uncheck:
                mark = "x" if number in check else " "
                first = own[0]
                own[0] = first[:BRACKET_COLUMN] + mark + first[BRACKET_COLUMN + 1 :]
            gap_end = items[number].start if number < len(items) else item.end
            kept.append(own + lines[item.end : gap_end])
        sections = list(self._sections)
        if not kept and not new_lines:
            del sections[index]
            _strip_trailing_blank(sections)
            return self._rebuild(sections=sections)
        if kept:
            # The last kept item ends the list, so drop the gap that separated
            # it from a following item that has been removed.
            last = kept[-1]
            while last and not last[-1].strip():
                last.pop()
        body = [line for item in kept for line in item]
        before = lines[: items[0].start]
        after = lines[items[-1].end :]
        sections[index] = _Section(ACCEPTANCE_CRITERIA, (*before, *body, *new_lines, *after))
        return self._rebuild(sections=sections)

    # -- helpers ---------------------------------------------------------

    def _section_index(self, name: str) -> int | None:
        return next((i for i, s in enumerate(self._sections) if s.name == name), None)

    def _insert_section(
        self, name: str, content: list[str], replace_existing: bool = False
    ) -> "Task":
        sections = list(self._sections)
        preamble = list(self._preamble)
        if replace_existing:
            existing = self._section_index(name)
            if existing is not None:
                del sections[existing]
                _strip_trailing_blank(sections)
        rank = SECTION_ORDER.index(name)
        position = next(
            (i for i, s in enumerate(sections) if SECTION_ORDER.index(s.name) > rank),
            len(sections),
        )
        is_last = position == len(sections)
        if is_last and sections and sections[-1].lines[-1].strip():
            sections[-1] = replace(sections[-1], lines=(*sections[-1].lines, "\n"))
        if position == 0 and not preamble:
            preamble = ["\n"]
        new = _Section(name, (f"## {name}\n", "\n", *content, *([] if is_last else ["\n"])))
        sections.insert(position, new)
        return self._rebuild(preamble=preamble, sections=sections)

    def _rebuild(
        self,
        fields: Sequence[_FieldSpan] | None = None,
        preamble: Sequence[str] | None = None,
        sections: Sequence[_Section] | None = None,
    ) -> "Task":
        draft = replace(
            self,
            _fields=self._fields if fields is None else tuple(fields),
            _preamble=self._preamble if preamble is None else tuple(preamble),
            _sections=self._sections if sections is None else tuple(sections),
        )
        return parse(draft.render())


# -- parsing --------------------------------------------------------------


def parse(text: str) -> Task:
    if "\r" in text:
        raise TaskError("CR line endings are not supported; use LF")
    if text and not text.endswith("\n"):
        raise TaskError("file must end with a newline")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0] != DELIMITER:
        raise TaskError("file must start with '---' frontmatter")
    try:
        close = lines.index(DELIMITER, 1)
    except ValueError:
        raise TaskError("frontmatter is not closed with '---'") from None
    fm_lines = lines[1:close]
    fields = _split_fields(fm_lines)
    frontmatter = _load_frontmatter(fm_lines, fields)
    preamble, sections = _split_sections(lines[close + 1 :], first_line=close + 2)
    criteria = _parse_criteria(sections)
    description = next((s for s in sections if s.name == DESCRIPTION), None)
    if description is None:
        raise TaskError("'## Description' section is required")
    if not "".join(description.lines[1:]).strip():
        raise TaskError("'## Description' must not be empty")
    return Task(frontmatter, tuple(fields), tuple(preamble), tuple(sections), criteria)


def new_task(
    title: str,
    created: date,
    description: str,
    criteria: Sequence[str],
    fields: dict[str, FieldValue],
) -> Task:
    """Build a new task. `fields` holds the optional frontmatter keys."""
    text = f"{DELIMITER}title: x\nstatus: todo\ncreated: {created.isoformat()}\n{DELIMITER}"
    text += f"\n## {DESCRIPTION}\n\n.\n"
    task = parse(text).with_field("title", title).with_section(DESCRIPTION, description)
    for key, value in fields.items():
        task = task.with_field(key, value)
    return task.with_criteria(add=criteria, remove=(), check=(), uncheck=())


def _split_fields(fm_lines: list[str]) -> list[_FieldSpan]:
    spans: list[_FieldSpan] = []
    key: str | None = None
    leading: list[str] = []
    current: list[str] = []
    pending: list[str] = []  # blank/comment lines: they belong to whatever follows
    for number, line in enumerate(fm_lines, start=2):
        match = KEY_LINE_RE.match(line)
        if match:
            spans.append(_FieldSpan(key, tuple(leading), tuple(current)))
            key, leading, current, pending = match[1], pending, [line], []
        elif not line.strip() or line[0] == "#":
            pending.append(line)
        elif line[0] in " \t-":
            current += [*pending, line]
            pending = []
        else:
            raise TaskError(
                f"line {number}: frontmatter keys must be plain 'key: value' at column 0"
            )
    spans.append(_FieldSpan(key, tuple(leading), tuple(current + pending)))
    keys = [s.key for s in spans if s.key is not None]
    duplicates = sorted({k for k in keys if keys.count(k) > 1})
    if duplicates:
        raise TaskError(f"duplicate frontmatter key {duplicates[0]!r}")
    return spans


def _load_frontmatter(fm_lines: list[str], fields: list[_FieldSpan]) -> Frontmatter:
    try:
        data = yaml.load("".join(fm_lines), Loader=_StringLoader)
    except yaml.YAMLError as error:
        raise TaskError(f"frontmatter is not valid YAML: {error}") from None
    if not isinstance(data, dict):
        raise TaskError("frontmatter must be a YAML mapping")
    data_keys: dict[str, Any] = data  # pyright: ignore[reportUnknownVariableType]
    if set(data_keys) != {s.key for s in fields if s.key is not None}:
        raise TaskError("frontmatter layout not understood: use one 'key: value' per line")
    try:
        return Frontmatter.model_validate(data_keys)
    except ValidationError as error:
        raise TaskError(_describe(error)) from None


def _describe(error: ValidationError) -> str:
    reasons: list[str] = []
    for detail in error.errors():
        where = ".".join(str(part) for part in detail["loc"])
        if detail["type"] == "extra_forbidden":
            reasons.append(f"unknown frontmatter key {where!r}")
        elif detail["type"] == "missing":
            reasons.append(f"frontmatter key {where!r} is required")
        else:
            message = str(detail["msg"]).removeprefix("Value error, ")
            reasons.append(f"{where}: {message}")
    return "; ".join(reasons)


def _split_sections(body: list[str], first_line: int) -> tuple[list[str], list[_Section]]:
    preamble: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    fence: str | None = None
    for number, line in enumerate(body, start=first_line):
        target = sections[-1][1] if sections else preamble
        if fence is not None:
            if re.fullmatch(rf" {{0,3}}{fence[0]}{{{len(fence)},}}[ \t]*\n?", line):
                fence = None
            target.append(line)
            continue
        opening = FENCE_OPEN_RE.match(line)
        if opening:
            fence = opening[1]
            target.append(line)
            continue
        heading = HEADING_RE.fullmatch(line.rstrip("\n"))
        if heading:
            indent, hashes, name = heading[1], heading[2], heading[3] or ""
            if len(hashes) == 1:
                raise TaskError(f"line {number}: '#' headings are not allowed; use '##' sections")
            if len(hashes) == 2:
                if indent:
                    raise TaskError(f"line {number}: '##' headings must start at column 0")
                if name not in SECTION_ORDER:
                    allowed = ", ".join(SECTION_ORDER)
                    raise TaskError(
                        f"line {number}: unknown section {name!r}; allowed: {allowed} "
                        "(use '###' for structure inside a section)"
                    )
                if any(existing == name for existing, _ in sections):
                    raise TaskError(f"line {number}: duplicate section {name!r}")
                sections.append((name, [line]))
                continue
        target.append(line)
    if any(line.strip() for line in preamble):
        raise TaskError("content before the first '##' section is not allowed")
    return preamble, [_Section(name, tuple(lines)) for name, lines in sections]


def _parse_criteria(sections: list[_Section]) -> tuple[Criterion, ...]:
    section = next((s for s in sections if s.name == ACCEPTANCE_CRITERIA), None)
    if section is None:
        return ()
    items: list[tuple[bool, list[str], int, int]] = []
    for offset, line in enumerate(section.lines[1:], start=1):
        stripped = line.strip()
        match = CRITERION_RE.fullmatch(line.rstrip("\n"))
        if not stripped:
            continue
        if match:
            if not match[2]:
                raise TaskError(f"acceptance criterion {len(items) + 1} has no text")
            items.append((match[1] != " ", [match[2]], offset, offset + 1))
        elif line[0] in " \t" and items:
            if LIST_MARKER_RE.match(stripped):
                raise TaskError(f"acceptance criterion {len(items)}: nested lists are not allowed")
            checked, text, start, _ = items[-1]
            items[-1] = (checked, [*text, stripped], start, offset + 1)
        else:
            raise TaskError(
                f"'## {ACCEPTANCE_CRITERIA}' may only contain '- [ ] ...' items; found {stripped!r}"
            )
    return tuple(Criterion(c, " ".join(t), s, e) for c, t, s, e in items)


# -- rendering --------------------------------------------------------------


def _render_field(key: str, value: str | list[str] | date) -> list[str]:
    if isinstance(value, date):
        return [f"{key}: {value.isoformat()}\n"]
    if isinstance(value, list):
        return [f"{key}:\n", *(f"  - {render_scalar(item)}\n" for item in value)]
    return [f"{key}: {render_scalar(value)}\n"]


def render_scalar(value: str) -> str:
    """Quote a string if any YAML reader would take it for something else."""
    if "\n" in value:
        raise TaskError(f"value {value!r} must be a single line")
    dumped = yaml.safe_dump(value, allow_unicode=True, width=float("inf"))
    plain = dumped.split("\n", 1)[0] == value
    if plain and not YAML_TYPED_RE.fullmatch(value):
        return value
    if '"' in value and "'" not in value:
        return f"'{value}'"
    return json.dumps(value, ensure_ascii=False)


def _insert_position(fields: list[_FieldSpan], key: str) -> int:
    rank = FIELD_ORDER.index(key)
    for index, span in enumerate(fields):
        if span.key is not None and FIELD_ORDER.index(span.key) > rank:
            return index
    return len(fields)


def _text_lines(text: str) -> list[str]:
    if "\r" in text:
        raise TaskError("CR line endings are not supported; use LF")
    text = text.strip("\n")
    if not text.strip():
        return []
    return [line.rstrip() + "\n" for line in text.split("\n")]


def _criterion_text(text: str) -> str:
    text = text.strip()
    if not text:
        raise TaskError("acceptance criterion must not be empty")
    if "\n" in text:
        raise TaskError("acceptance criterion must be a single line")
    return text


def _strip_trailing_blank(sections: list[_Section]) -> None:
    if not sections:
        return
    lines = list(sections[-1].lines)
    while len(lines) > 1 and not lines[-1].strip():
        lines.pop()
    sections[-1] = replace(sections[-1], lines=tuple(lines))
