"""Resolve a stable, human-readable actor name from coding-agent environments."""

import hashlib
import json
import os
import re
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path
from typing import cast

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
_SESSION_VARIABLES = (
    "CLAUDE_CODE_SESSION_ID",
    "PI_SESSION_ID",
    "CODEX_THREAD_ID",
    "CODEX_SESSION_ID",
)


def actor(environment: Mapping[str, str] | None = None) -> str:
    """Return the explicit or harness-derived name for this actor."""
    env = os.environ if environment is None else environment
    if override := env.get("CHITTY_ACTOR", "").strip():
        return override
    for variable in _SESSION_VARIABLES:
        if identity := env.get(variable, "").strip():
            return _readable_name(variable, identity)
    names = ", ".join(_SESSION_VARIABLES)
    raise ChittyError(f"cannot determine actor; set CHITTY_ACTOR or provide one of {names}")


def _readable_name(source: str, identity: str) -> str:
    digest = hashlib.sha256(f"{source}:{identity}".encode()).digest()
    return f"{_ADJECTIVES[digest[0] % len(_ADJECTIVES)]}-{_ANIMALS[digest[1] % len(_ANIMALS)]}"


def pi_settings_path(environment: Mapping[str, str] | None = None) -> Path:
    """Return Pi's settings location, respecting HOME for isolated environments."""
    env = os.environ if environment is None else environment
    return Path(env.get("HOME", str(Path.home()))) / ".pi" / "agent" / "settings.json"


def enable_pi_session_environment() -> Path | None:
    """Enable Pi's session environment, preserving every unrelated settings byte."""
    path = pi_settings_path()
    if not path.exists():
        return None
    text = path.read_text()
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ChittyError(f"Pi settings at {path} must be a JSON object")
    settings = cast(dict[str, object], parsed)
    if settings.get("exposeSessionEnvironment") is True:
        return None
    key = r'("exposeSessionEnvironment"\s*:\s*)(true|false|null|"[^"]*"|\d+)'
    if re.search(key, text):
        updated = re.sub(key, r"\g<1>true", text, count=1)
    else:
        closing = re.search(r"(?s)\}(\s*)\Z", text)
        assert closing is not None
        content = text[: closing.start()].rstrip()
        separator = "," if settings else ""
        updated = f'{content}{separator}\n  "exposeSessionEnvironment": true\n}}{closing.group(1)}'
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
    if target.exists() and target.read_bytes() == source:
        return None
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(source)
    return target


def pi_session_environment_missing(environment: Mapping[str, str] | None = None) -> bool:
    """Whether a Pi agent lacks the identity its shell session should expose."""
    env = os.environ if environment is None else environment
    return env.get("PI_CODING_AGENT") == "true" and not env.get("PI_SESSION_ID")
