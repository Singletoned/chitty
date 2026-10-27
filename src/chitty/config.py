"""Repo `chitty.toml` and user-level `contexts.toml`."""

import os
import re
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator

from chitty.errors import ChittyError
from chitty.ids import PREFIX_RE

CONFIG_NAME = "chitty.toml"
PYPROJECT_NAME = "pyproject.toml"
BACKLOG_DIR = "chitty"
ROOT_ENV = "CHITTY_ROOT"
CONTEXT_NAME_RE = re.compile(r"[a-z0-9][a-z0-9_-]*")
PROJECT_NAME_RE = re.compile(r"[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?")
RESERVED_CONTEXT_NAMES = ("archive",)
INITIAL_CONFIG = """\
format = 1
default_context = "tasks"
project = "{project}"
autocommit = false
review = true
# autoformat = "mdformat"
# archive = "move"  # or "delete"; retain completed files or delete them

[contexts.tasks]
prefix = "{prefix}"

[contexts.human]
prefix = "HUMAN"
"""


class ContextConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    prefix: str

    @field_validator("prefix")
    @classmethod
    def _prefix(cls, value: str) -> str:
        if not PREFIX_RE.fullmatch(value):
            raise ValueError(f"{value!r} must be upper-case letters only, e.g. TASK")
        return value


class RepoConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    format: Literal[1]
    default_context: str
    project: str | None = None
    autocommit: bool
    review: bool = True
    autoformat: str | None = None
    archive: Literal["move", "delete"] = "move"
    contexts: dict[str, ContextConfig]

    @field_validator("project")
    @classmethod
    def _project(cls, value: str | None) -> str | None:
        if value is not None and not PROJECT_NAME_RE.fullmatch(value):
            raise ValueError(
                "must use lowercase letters, digits, '.', '_' or '-' and start/end alphanumeric"
            )
        return value

    @field_validator("autoformat")
    @classmethod
    def _autoformat(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be empty")
        return value

    @model_validator(mode="after")
    def _consistent(self) -> "RepoConfig":
        for name in self.contexts:
            if not CONTEXT_NAME_RE.fullmatch(name) or name in RESERVED_CONTEXT_NAMES:
                raise ValueError(f"context name {name!r} is not allowed")
        if self.default_context not in self.contexts:
            raise ValueError(f"default_context {self.default_context!r} is not in [contexts]")
        prefixes = [c.prefix for c in self.contexts.values()]
        duplicates = sorted({p for p in prefixes if prefixes.count(p) > 1})
        if duplicates:
            raise ValueError(f"prefix {duplicates[0]!r} is used by more than one context")
        return self


class UserContext(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    repo: str
    context: str | None = None


class UserContexts(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    contexts: dict[str, UserContext] = {}


def find_root(start: Path) -> Path:
    """`CHITTY_ROOT` if set, else the nearest ancestor with Chitty config."""
    root = search_root(start)
    if root is None:
        raise ChittyError(
            f"no {CONFIG_NAME} or [tool.chitty] in {PYPROJECT_NAME} in {start} or any parent "
            "(run `chitty init`)"
        )
    return root


def search_root(start: Path) -> Path | None:
    """Like find_root, but None when no Chitty config is found by walking up."""
    override = os.environ.get(ROOT_ENV)
    if override:
        root = Path(override).expanduser().resolve()
        if _config_source(root) is None:
            raise ChittyError(f"{ROOT_ENV}={override} has no Chitty configuration")
        return root
    start = start.resolve()
    for directory in (start, *start.parents):
        if _config_source(directory) is not None:
            return directory
    return None


def load_repo_config(root: Path) -> RepoConfig:
    source = _config_source(root)
    if source is None:
        raise ChittyError(f"no Chitty configuration in {root}")
    if source.name == CONFIG_NAME:
        return _load(source, RepoConfig)
    try:
        data = tomllib.loads(source.read_text())
    except tomllib.TOMLDecodeError as error:
        raise ChittyError(f"{source}: invalid TOML: {error}") from None
    try:
        chitty = data["tool"]["chitty"]
    except (KeyError, TypeError):
        raise ChittyError(f"{source}: [tool.chitty] is required") from None
    return _validate_data(chitty, source, RepoConfig)


def _config_source(root: Path) -> Path | None:
    config = root / CONFIG_NAME
    pyproject = root / PYPROJECT_NAME
    has_config = config.is_file()
    has_pyproject_config = _has_pyproject_config(pyproject)
    if has_config and has_pyproject_config:
        raise ChittyError(f"{root}: both {CONFIG_NAME} and {PYPROJECT_NAME} contain Chitty config")
    if has_config:
        return config
    if has_pyproject_config:
        return pyproject
    return None


def _has_pyproject_config(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError:
        return False
    return isinstance(data.get("tool"), dict) and "chitty" in data["tool"]


def inbox_path(project: str) -> Path:
    """Machine-local inbox directory for a registered project."""
    base = Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser()
    return base / "chitty" / "inbox" / project


def registered_projects() -> list[str]:
    base = inbox_path("_").parent
    return sorted(path.name for path in base.iterdir() if path.is_dir()) if base.exists() else []


def register_project(project: str, root: Path | None) -> Path:
    """Claim a project inbox name, refusing ownership by another repository."""
    directory = inbox_path(project)
    owner = directory / "repo"
    resolved = str(root.resolve()) if root is not None else ""
    current = owner.read_text().strip() if owner.exists() else ""
    if current not in ("", resolved):
        raise ChittyError(
            f"project {project!r} is registered to {current}; choose explicit project = name"
        )
    directory.mkdir(parents=True, exist_ok=True)
    if resolved:
        owner.write_text(resolved + "\n")
    elif not owner.exists():
        owner.write_text("")
    return directory


def user_contexts_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or "~/.config"
    return Path(base).expanduser() / "chitty" / "contexts.toml"


def load_user_contexts() -> UserContexts:
    path = user_contexts_path()
    if not path.exists():
        return UserContexts()
    return _load(path, UserContexts)


def validate_repo_config(text: str, source: Path) -> RepoConfig:
    return _validate(text, source, RepoConfig)


def _load[M: BaseModel](path: Path, model: type[M]) -> M:
    return _validate(path.read_text(), path, model)


def _validate[M: BaseModel](text: str, path: Path, model: type[M]) -> M:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ChittyError(f"{path}: invalid TOML: {error}") from None
    return _validate_data(data, path, model)


def _validate_data[M: BaseModel](data: object, path: Path, model: type[M]) -> M:
    try:
        return model.model_validate(data)
    except ValidationError as error:
        reasons = [
            f"{'.'.join(str(p) for p in e['loc']) or 'config'}: "
            + str(e["msg"]).removeprefix("Value error, ")
            for e in error.errors()
        ]
        raise ChittyError(f"{path}: {'; '.join(reasons)}") from None
