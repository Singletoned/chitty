"""Require setup changes on branches to carry a version bump."""

import re
import subprocess
import sys
from pathlib import Path

MAIN_REF = "refs/heads/main"
VERSION_FILE = "src/chitty/__init__.py"
CONFIG_FILE = "src/chitty/config.py"
INITIAL_CONFIG_RE = re.compile(
    r"(?ms)^INITIAL_CONFIG\s*=\s*(?P<quote>'''|\"\"\")(?P<text>.*?)(?P=quote)"
)
VERSION_RE = re.compile(r"^__version__\s*=\s*[\"\']([^\"\']+)[\"\']\s*$", re.MULTILINE)
WATCHED_FILES = (
    "src/chitty/guide.md",
    "src/chitty/integrations/pi/chitty.ts",
)


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return result.stdout


def version(text: str, source: str) -> tuple[int, ...]:
    match = VERSION_RE.search(text)
    if match is None:
        raise ValueError(f"could not find __version__ in {source}")
    value = match.group(1)
    try:
        return tuple(int(part) for part in value.split("."))
    except ValueError as error:
        raise ValueError(f"invalid dotted-integer version {value!r} in {source}") from error


def current_file(path: str) -> str | None:
    file = Path(path)
    return file.read_text() if file.exists() else None


def initial_config(text: str | None, source: str) -> str:
    if text is None:
        raise ValueError(f"could not find {CONFIG_FILE} in {source}")
    match = INITIAL_CONFIG_RE.search(text)
    if match is None:
        raise ValueError(f"could not find INITIAL_CONFIG in {source}")
    return match.group("text")


def changed_files(base: str) -> list[str]:
    output = git("diff", "--name-only", base, "--", *WATCHED_FILES, "src/chitty/roles")
    changed = set(output.splitlines())
    current_config = current_file(CONFIG_FILE)
    base_config = git("show", f"{base}:{CONFIG_FILE}")
    if current_config is None or initial_config(current_config, "working tree") != initial_config(
        base_config, f"{base}:{CONFIG_FILE}"
    ):
        changed.add(CONFIG_FILE)
    return sorted(changed)


def main() -> int:
    try:
        git("show-ref", "--verify", "--quiet", MAIN_REF)
    except subprocess.CalledProcessError:
        print("check_version_bump: no refs/heads/main; passing", file=sys.stderr)
        return 0

    if git("branch", "--show-current").strip() == "main":
        return 0

    base = git("merge-base", "HEAD", MAIN_REF).strip()
    files = changed_files(base)
    if not files:
        return 0

    current = version(Path(VERSION_FILE).read_text(), "working tree")
    main = version(git("show", f"{MAIN_REF}:{VERSION_FILE}"), f"{MAIN_REF}:{VERSION_FILE}")
    if current <= main:
        current_text = ".".join(str(part) for part in current)
        main_text = ".".join(str(part) for part in main)
        print(
            "check_version_bump: changed files require a version above "
            f"main ({main_text}), but working tree has {current_text}:",
            file=sys.stderr,
        )
        print("  " + "\n  ".join(files), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"check_version_bump: {error}", file=sys.stderr)
        raise SystemExit(1) from error
