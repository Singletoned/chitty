"""Resolve a stable, human-readable actor name from coding-agent environments."""

import hashlib
import json
import os
import re
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path

from chitty.errors import ChittyError

_ADJECTIVES = (
    "amber",
    "brisk",
    "calm",
    "daring",
    "eager",
    "frosty",
    "golden",
    "honest",
    "ivory",
    "jolly",
    "kind",
    "lively",
    "mellow",
    "nimble",
    "opal",
    "proud",
)
_ANIMALS = (
    "badger",
    "crane",
    "dolphin",
    "falcon",
    "gecko",
    "heron",
    "ibis",
    "jaguar",
    "koala",
    "lynx",
    "marten",
    "otter",
    "panda",
    "quail",
    "raven",
    "stoat",
)
_SESSION_IDENTITIES = (
    ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"),
    ("CHITTY_PI_SESSION_ID", "PI_SESSION_ID"),
    ("PI_SESSION_ID", "PI_SESSION_ID"),
    ("CODEX_THREAD_ID", "CODEX_THREAD_ID"),
    ("CODEX_SESSION_ID", "CODEX_SESSION_ID"),
)


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


def install_pi_extension(environment: Mapping[str, str] | None = None) -> Path | None:
    """Install Chitty's Pi extension when a Pi agent directory already exists."""
    settings = pi_settings_path(environment)
    agent = settings.parent
    if not agent.is_dir():
        return None
    target = agent / "extensions" / "chitty.ts"
    source = files("chitty.integrations.pi").joinpath("chitty.ts").read_bytes()
    if target.exists():
        if target.read_bytes() == source:
            return None
        raise ChittyError(
            f"Pi extension at {target} differs from Chitty's shipped extension and may "
            "contain local edits; review the changes, then replace or remove it before "
            "running chitty init again"
        )
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(source)
    return target


def pi_session_environment_missing(environment: Mapping[str, str] | None = None) -> bool:
    """Whether a Pi agent lacks the identity its shell session should expose."""
    env = os.environ if environment is None else environment
    return env.get("PI_CODING_AGENT") == "true" and not env.get("CHITTY_PI_SESSION_ID")
