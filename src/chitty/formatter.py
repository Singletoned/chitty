"""Run configured task-file formatters."""

import shlex
import subprocess
from collections.abc import Sequence
from pathlib import Path

from chitty.errors import ChittyError


def run(root: Path, command: str, paths: Sequence[Path]) -> None:
    """Run formatter command against paths without invoking a shell."""
    arguments = shlex.split(command)
    if not arguments:
        raise ChittyError("autoformat command must not be empty")
    result = subprocess.run(
        [*arguments, *(str(path) for path in paths)],
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        shown = " ".join(arguments)
        raise ChittyError(f"autoformat failed: `{shown}` in {root}:\n{result.stderr.strip()}")
