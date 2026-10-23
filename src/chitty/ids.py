"""Task IDs, filenames and slugs."""

import re
from collections.abc import Iterable
from dataclasses import dataclass

SLUG_MAX_LENGTH = 60

ID_RE = re.compile(r"(?P<prefix>[A-Z]+)-(?P<number>[1-9][0-9]*)")
PREFIX_RE = re.compile(r"[A-Z]+")
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NUMBER_RE = re.compile(r"[1-9][0-9]*")
FILENAME_SEPARATOR = "--"
SUFFIX = ".md"


class IdError(ValueError):
    pass


@dataclass(frozen=True, order=True)
class TaskId:
    prefix: str
    number: int

    def __str__(self) -> str:
        return f"{self.prefix}-{self.number}"

    @classmethod
    def parse(cls, text: str) -> "TaskId":
        match = ID_RE.fullmatch(text)
        if match is None:
            raise IdError(f"invalid task ID {text!r}: expected PREFIX-N, e.g. TASK-13")
        return cls(match["prefix"], int(match["number"]))


def resolve(text: str, default_prefix: str) -> TaskId:
    """Parse a user-supplied reference: `TASK-13`, or bare `13` for the default prefix."""
    if NUMBER_RE.fullmatch(text):
        return TaskId(default_prefix, int(text))
    return TaskId.parse(text)


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:SLUG_MAX_LENGTH].rstrip("-")


def filename(task_id: TaskId, slug: str) -> str:
    if not slug:
        return f"{task_id}{SUFFIX}"
    return f"{task_id}{FILENAME_SEPARATOR}{slug}{SUFFIX}"


def parse_filename(name: str) -> tuple[TaskId, str]:
    """Split `TASK-13--add-search.md` into its ID and slug."""
    if not name.endswith(SUFFIX):
        raise IdError(f"task filename {name!r} must end with {SUFFIX}")
    stem = name.removesuffix(SUFFIX)
    id_text, _, slug = stem.partition(FILENAME_SEPARATOR)
    task_id = TaskId.parse(id_text)
    if FILENAME_SEPARATOR in stem and not SLUG_RE.fullmatch(slug):
        raise IdError(
            f"task filename {name!r} has an invalid slug {slug!r}: "
            "expected lowercase letters, digits and single hyphens"
        )
    return task_id, slug


def next_number(existing: Iterable[int]) -> int:
    return max(existing, default=0) + 1
