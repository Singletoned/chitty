"""Choose the next published version from tagged ticket changes."""

import re
import subprocess
import sys
from pathlib import Path

from chitty.model import parse

VERSION_FILE = Path("src/chitty/__init__.py")
VERSION_RE = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']$', re.MULTILINE)
TAG_RE = re.compile(r"^v(\d+(?:\.\d+)*)$")


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout


def version(text: str, source: str) -> tuple[int, ...]:
    match = VERSION_RE.search(text)
    if match is None:
        raise ValueError(f"could not find __version__ in {source}")
    try:
        return tuple(int(part) for part in match.group(1).split("."))
    except ValueError as error:
        raise ValueError(f"invalid version in {source}: {match.group(1)!r}") from error


def tag_versions() -> list[tuple[tuple[int, ...], str]]:
    tags = git("tag", "--list", "v*").splitlines()
    if not tags:
        raise ValueError("no v* tags found")
    versions = []
    for tag in tags:
        match = TAG_RE.fullmatch(tag)
        if match is None:
            raise ValueError(f"tag {tag!r} is not a dotted-integer v* version")
        versions.append((tuple(int(part) for part in match.group(1).split(".")), tag))
    return versions


def changed_ticket_paths(tag: str) -> list[Path]:
    changed = git("diff", "--name-only", f"{tag}..HEAD", "--", "chitty/").splitlines()
    paths = []
    for name in changed:
        path = Path(name)
        # Deleted tickets have no labels left to read; archive-by-move keeps the
        # useful case available, while deletion is intentionally accepted.
        if path.suffix == ".md" and path.exists():
            paths.append(path)
    return paths


def main() -> None:
    tags = tag_versions()
    tag_version, tag = max(tags)
    current_version = version(VERSION_FILE.read_text(), str(VERSION_FILE))
    base = max(tag_version, current_version)

    labelled: list[Path] = []
    for path in changed_ticket_paths(tag):
        task = parse(path.read_text())
        if "needs-minor" in task.frontmatter.labels:
            labelled.append(path)

    if labelled:
        next_version = (base[0], base[1] + 1, 0)
    else:
        next_version = (*base[:2], base[2] + 1)
    print(".".join(str(part) for part in next_version))
    for path in labelled:
        print(f"needs-minor: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
