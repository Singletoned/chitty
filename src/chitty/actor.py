"""Resolve a stable, human-readable actor name from coding-agent environments."""

import hashlib
import json
import os
import re
import sys
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path

from chitty import __version__
from chitty.config import _version_key  # pyright: ignore[reportPrivateUsage]
from chitty.errors import ChittyError

_ADJECTIVES = (
    "able",
    "brisk",
    "calm",
    "daring",
    "eager",
    "friendly",
    "golden",
    "honest",
    "intrepid",
    "jolly",
    "kind",
    "lively",
    "mellow",
    "nimble",
    "open",
    "plucky",
    "quick",
    "rosy",
    "sunny",
    "tidy",
    "upbeat",
    "vivid",
    "witty",
    "youthful",
    "zesty",
)
_ANIMALS = (
    "adder",
    "badger",
    "crane",
    "dormouse",
    "eel",
    "falcon",
    "gannet",
    "heron",
    "ibis",
    "jay",
    "kestrel",
    "lapwing",
    "marten",
    "newt",
    "otter",
    "puffin",
    "quail",
    "raven",
    "stoat",
    "toad",
    "urchin",
    "vole",
    "wren",
    "yellowhammer",
    "zander",
)

_PI_EXTENSION_STATE = "chitty-extension.sha256"
_PI_EXTENSION_STATE_LINES = 2

_SESSION_IDENTITIES = (
    ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"),
    ("CHITTY_PI_SESSION_ID", "PI_SESSION_ID"),
    ("PI_SESSION_ID", "PI_SESSION_ID"),
    ("CODEX_THREAD_ID", "CODEX_THREAD_ID"),
    ("CODEX_SESSION_ID", "CODEX_SESSION_ID"),
)


def run_actor(identity: str) -> str:
    """Return the readable actor name for a `chitty run` session."""
    return _readable_name("CHITTY_RUN", identity)


def actor(environment: Mapping[str, str] | None = None) -> str:
    """Return the explicit or harness-derived name for this actor."""
    env = os.environ if environment is None else environment
    if override := env.get("CHITTY_ACTOR", "").strip():
        return override
    for variable, source in _SESSION_IDENTITIES:
        if identity := env.get(variable, "").strip():
            return _readable_name(source, identity)
    names = ", ".join(variable for variable, _ in _SESSION_IDENTITIES)
    raise ChittyError(f"cannot determine actor; set CHITTY_ACTOR or provide one of {names}")


def _readable_name(source: str, identity: str) -> str:
    digest = hashlib.sha256(f"{source}:{identity}".encode()).digest()
    return f"{_ADJECTIVES[digest[0] % len(_ADJECTIVES)]}-{_ANIMALS[digest[1] % len(_ANIMALS)]}"


def pi_settings_path(environment: Mapping[str, str] | None = None) -> Path:
    """Return Pi's settings location, respecting its configured agent directory."""
    env = os.environ if environment is None else environment
    agent = env.get("PI_CODING_AGENT_DIR")
    if agent:
        return Path(agent) / "settings.json"
    return Path(env.get("HOME", str(Path.home()))) / ".pi" / "agent" / "settings.json"


def remove_pi_session_environment() -> Path | None:
    """Remove Chitty's obsolete Pi setting without changing other settings."""
    path = pi_settings_path()
    if not path.exists():
        return None
    text = path.read_text()
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ChittyError(f"Pi settings at {path} must be a JSON object")
    if "exposeSessionEnvironment" not in parsed:
        return None
    pattern = r'(?m)(?:,\n|\n)[ \t]*"exposeSessionEnvironment"\s*:\s*(?:true|false)(?=\n[ \t]*\})'
    updated, count = re.subn(pattern, "", text, count=1)
    if count != 1:
        raise ChittyError(f"cannot safely remove obsolete Pi setting from {path}")
    path.write_text(updated)
    return path


def _pi_extension_files(
    environment: Mapping[str, str] | None = None,
) -> tuple[Path, Path, bytes] | None:
    agent = pi_settings_path(environment).parent
    if not agent.is_dir():
        return None
    source = files("chitty.integrations.pi").joinpath("chitty.ts").read_bytes()
    return agent / "extensions" / "chitty.ts", agent / _PI_EXTENSION_STATE, source


def _extension_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _validate_pi_extension(files: tuple[Path, Path, bytes] | None) -> None:
    if files is None:
        return
    target, state, source = files
    if not target.exists() or target.read_bytes() == source:
        return
    expected_hash = _extension_hash(target.read_bytes())
    if state.exists() and state.read_text().splitlines()[:1] == [expected_hash]:
        return
    raise ChittyError(
        f"Pi extension at {target} differs from Chitty's shipped extension and may "
        "contain local edits; review the changes, then replace or remove it before "
        "running chitty init again"
    )


def validate_pi_extension(environment: Mapping[str, str] | None = None) -> None:
    """Raise before setup writes when a Pi extension has local edits."""
    _validate_pi_extension(_pi_extension_files(environment))


def _installed_extension_version(state: Path) -> str | None:
    """Return the recorded version, treating old state formats as older."""
    try:
        lines = state.read_text().splitlines()
        version = lines[1] if len(lines) >= _PI_EXTENSION_STATE_LINES else None
        if version is not None:
            _version_key(version)
        return version
    except (ChittyError, OSError, UnicodeError):
        return None


def install_pi_extension(environment: Mapping[str, str] | None = None) -> Path | None:
    """Install or update Chitty's unedited Pi extension."""
    extension = _pi_extension_files(environment)
    if extension is None:
        return None
    target, state, source = extension
    _validate_pi_extension(extension)
    installed_version = _installed_extension_version(state) if target.exists() else None
    if installed_version is not None and _version_key(installed_version) > _version_key(
        __version__
    ):
        print(
            f"Chitty {__version__} is older than the installed Pi extension from Chitty "
            f"{installed_version}; upgrade Chitty, or delete {target} and {state} together",
            file=sys.stderr,
        )
        return None
    source_hash = _extension_hash(source)
    if (
        target.exists()
        and target.read_bytes() == source
        and state.exists()
        and state.read_text().strip() == f"{source_hash}\n{__version__}"
    ):
        return None
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(source)
    state.write_text(f"{source_hash}\n{__version__}\n")
    return target


def pi_session_environment_missing(environment: Mapping[str, str] | None = None) -> bool:
    """Whether a Pi agent lacks the identity its shell session should expose.

    `CHITTY_ACTOR` supplies one, as `chitty run` does for print-mode Pi.
    """
    env = os.environ if environment is None else environment
    return (
        env.get("PI_CODING_AGENT") == "true"
        and not env.get("CHITTY_PI_SESSION_ID")
        and not env.get("CHITTY_ACTOR", "").strip()
    )
