"""Advice about newer released versions of Chitty."""

import json
import sys
import time
import urllib.error
import urllib.request
from importlib import metadata
from importlib.metadata import PackageNotFoundError
from pathlib import Path

from chitty import __version__
from chitty.config import chitty_data_path, version_key
from chitty.errors import ChittyError

PYPI_URL = "https://pypi.org/pypi/chitty/json"
UPGRADE_RETRY_SECONDS = 60
REQUEST_TIMEOUT = 2
ALERT = "chitty {version} is out: run uv tool upgrade chitty"


def check_for_upgrade() -> None:
    """Print a release alert, if checking is due and succeeds."""
    if _is_editable_install():
        return
    path = chitty_data_path() / "pending-release"
    try:
        _check(path)
    except (ChittyError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        # Upgrade advice must never affect the command when its file is unreadable.
        return


def _check(path: Path) -> None:
    if not path.exists():
        return
    lines = path.read_text().splitlines()
    if not lines:
        path.unlink()
        return
    pending = lines[0].strip()
    try:
        pending_key = version_key(pending)
        running_key = version_key(__version__)
    except (ChittyError, TypeError, ValueError):
        path.unlink()
        return
    if running_key >= pending_key:
        path.unlink()
        return
    if len(lines) > 1 and lines[1].strip() == "out":
        _alert(pending)
        return
    if path.stat().st_mtime > _now() - UPGRADE_RETRY_SECONDS:
        return
    path.touch()
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=REQUEST_TIMEOUT) as response:
            released = json.loads(response.read())["info"]["version"]
    except (
        KeyError,
        TypeError,
        ValueError,
        OSError,
        TimeoutError,
        urllib.error.URLError,
    ):
        # A failed request is harmless advice; the touched file limits retries.
        return
    if version_key(released) >= pending_key:
        path.write_text(f"{released}\nout\n")
        _alert(released)


def _is_editable_install() -> bool:
    try:
        direct_url = metadata.distribution("chitty").read_text("direct_url.json")
        return bool(direct_url and json.loads(direct_url).get("dir_info", {}).get("editable"))
    except (
        AttributeError,
        PackageNotFoundError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        TypeError,
    ):
        return False


def _alert(version: str) -> None:
    print(ALERT.format(version=version), file=sys.stderr)


def _now() -> float:
    return time.time()
