"""Repo `chitty.toml` and user-level `contexts.toml`."""

import os
import re
import subprocess
import sys
import tomllib
from collections.abc import Mapping
from functools import cache
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from chitty import __version__, git
from chitty.errors import ChittyError
from chitty.ids import PREFIX_RE

CONFIG_NAME = "chitty.toml"
PYPROJECT_NAME = "pyproject.toml"
BACKLOG_DIR = "chitty"
ROOT_ENV = "CHITTY_ROOT"
CHITTY_VERSION = __version__
LIST_WIDTH = 100
DEFAULT_AGENT_TIMEOUT = 7200
DEFAULT_COMMAND_TIMEOUT = 3600
LAST_RUNNER_DEFAULT_VERSION = "0.5.0"
LAST_SHARED_PLANNING_VERSION = "0.8.0"
CONTEXT_NAME_RE = re.compile(r"[a-z0-9][a-z0-9_-]*")
PROJECT_NAME_RE = re.compile(r"[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?")
RESERVED_CONTEXT_NAMES = ("archive",)
_WARNED_UNKNOWN_KEYS: set[Path] = set()
INITIAL_CONFIG = """\
format = 1
default_context = "tasks"
project = {project}
chitty_version = "{version}"
autocommit = false
review = true
# autoformat = "taidy format" # run on every written task file
# setup = "make install" # run in every ticket worktree before the agent starts
# check = "make check" # validate the ticket worktree before the agent starts
# agent_command = "pi -p {{prompt}}"
# work_model = "provider/model" # default for work sessions when the command has no model
# review_model = "provider/model" # default for review sessions when the command has no model
# rebase_model = "provider/model" # default for rebase sessions when the command has no model
archive = "move" # or "delete"; retain completed files or delete them

[contexts.tasks]
prefix = "TASK"

[contexts.human]
prefix = "HUMAN"
review = false

[contexts.backlog]
prefix = "BACKLOG"
random_ids = true

[agent_commands]
"""


def agent_command_warnings(
    agent_command: str | None, agent_commands: Mapping[str, str]
) -> list[str]:
    commands = [("agent_command", agent_command)]
    commands.extend((f"agent_commands.{name}", value) for name, value in sorted(agent_commands.items()))
    return [
        f"{setting} has no {{prompt}}; Chitty no longer manages the Pi extension that "
        "`{mode}`/`{id}` commands relied on, so use a print-mode command such as `pi -p {prompt}`"
        for setting, command in commands
        if command is not None and command.strip() and "{prompt}" not in command
    ]


class ContextConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    prefix: str
    old_prefixes: list[str] = []
    review: bool | None = None
    # Number new tickets randomly instead of sequentially, so tickets raised on
    # different branches cannot collide: only `main` hands out sequential IDs.
    random_ids: bool = False

    @field_validator("prefix")
    @classmethod
    def _prefix(cls, value: str) -> str:
        if not PREFIX_RE.fullmatch(value):
            raise ValueError(f"{value!r} must be upper-case letters only, e.g. TASK")
        return value

    @field_validator("old_prefixes")
    @classmethod
    def _old_prefixes(cls, values: list[str]) -> list[str]:
        for value in values:
            cls._prefix(value)
        return values


class RepoConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    format: Literal[1]
    default_context: str
    project: str | None = None
    main_branch: str = "main"
    chitty_version: str | None = None
    workflow: str
    autocommit: bool
    review: bool
    autoformat: str | None = None
    setup: str | None = None
    check: str | None = None
    landing_check: str | None = None
    agent_command: str | None = None
    error_reporter: str | None = None
    agent_timeout: int = Field(default_factory=lambda: DEFAULT_AGENT_TIMEOUT, ge=0)
    command_timeout: int = Field(default_factory=lambda: DEFAULT_COMMAND_TIMEOUT, ge=0)
    agent_commands: dict[str, str] = {}
    work_model: str | None = None
    review_model: str | None = None
    rebase_model: str | None = None
    archive: Literal["move", "delete"] = "move"
    job_order: list[str] | None = None
    priorities: list[str] = ["high", "medium", "", "low"]
    protected_paths: list[str] = []
    list_width: int = Field(default=LIST_WIDTH, gt=0)
    contexts: dict[str, ContextConfig]

    @model_validator(mode="before")
    @classmethod
    def _workflow_defaults(cls, data: object) -> object:
        """Resolve omitted workflow and review defaults before frozen validation."""
        if not isinstance(data, Mapping):
            return data
        settings = dict(cast(Mapping[str, object], data))
        version = settings.get("chitty_version")
        setup_version = version if isinstance(version, str) else None
        if "workflow" not in settings:
            settings["workflow"] = resolve_workflow(None, setup_version)
        if "review" not in settings:
            settings["review"] = settings["workflow"] == "runner"
        return settings

    @field_validator("workflow", mode="before")
    @classmethod
    def _workflow(cls, value: object) -> str:
        if not isinstance(value, str) or value not in {"tickets", "runner"}:
            raise ValueError("must be a string: 'tickets' or 'runner'")
        return value

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

    @field_validator("work_model", "review_model", "rebase_model")
    @classmethod
    def _model(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("setup", "check", "landing_check", "error_reporter")
    @classmethod
    def _command(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be empty")
        return value

    @field_validator("protected_paths")
    @classmethod
    def _protected_paths(cls, paths: list[str]) -> list[str]:
        for entry in paths:
            parts = entry.split("/")
            if (
                not entry.strip()
                or entry.startswith("/")
                or entry.endswith("/")
                or "\\" in entry
                or any(part in {"", ".", ".."} for part in parts)
            ):
                raise ValueError(f"invalid protected path {entry!r}")
        return paths

    @field_validator("job_order")
    @classmethod
    def _job_order(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        allowed = {"review", "doing", "todo"}
        invalid = [status for status in value if status not in allowed]
        if invalid:
            raise ValueError(f"job_order contains invalid status {invalid[0]!r}")
        if not value:
            raise ValueError("job_order must not be empty")
        if len(set(value)) != len(value):
            raise ValueError("job_order must not repeat statuses")
        return value

    @field_validator("priorities")
    @classmethod
    def _priorities(cls, value: list[str]) -> list[str]:
        if value.count("") != 1:
            raise ValueError('priorities must contain "" exactly once, to place tickets with no priority')
        seen: set[str] = set()
        for name in value:
            if name in seen:
                raise ValueError(f"priorities lists {name!r} twice")
            if name != name.strip() or len(name.splitlines()) > 1:
                raise ValueError(
                    f"priority {name!r} must be one word or phrase on one line, "
                    "without surrounding spaces"
                )
            seen.add(name)
        return value

    @model_validator(mode="after")
    def _consistent(self) -> "RepoConfig":
        for name in self.contexts:
            if not CONTEXT_NAME_RE.fullmatch(name) or name in RESERVED_CONTEXT_NAMES:
                raise ValueError(f"context name {name!r} is not allowed")
        if self.default_context not in self.contexts:
            raise ValueError(f"default_context {self.default_context!r} is not in [contexts]")
        prefixes = [p for c in self.contexts.values() for p in (c.prefix, *c.old_prefixes)]
        duplicates = sorted({p for p in prefixes if prefixes.count(p) > 1})
        if duplicates:
            raise ValueError(f"prefix {duplicates[0]!r} is used by more than one context or repeated")
        return self


class UserContext(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    repo: str
    context: str | None = None


class UserContexts(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    contexts: dict[str, UserContext] = {}


def landing_command(check: str | None, landing_check: str | None) -> str:
    """Choose the command used to validate a branch before landing."""
    if landing_check is not None:
        return landing_check
    if check is None:
        raise ChittyError("check is required when landing_check is unset")
    return check


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
        if config_source(root) is None:
            raise ChittyError(f"{ROOT_ENV}={override} has no Chitty configuration")
        return root
    start = start.resolve()
    for directory in (start, *start.parents):
        if config_source(directory) is not None:
            return directory
    return None


def load_repo_config(root: Path) -> RepoConfig:
    source = config_source(root)
    if source is None:
        raise ChittyError(f"no Chitty configuration in {root}")
    try:
        data = tomllib.loads(source.read_text())
    except tomllib.TOMLDecodeError as error:
        raise ChittyError(f"{source}: invalid TOML: {error}") from None
    if source.name != CONFIG_NAME:
        try:
            data = data["tool"]["chitty"]
        except (KeyError, TypeError):
            raise ChittyError(f"{source}: [tool.chitty] is required") from None
    data = _remove_unknown_configuration_keys(data, source)
    return _validate_data(data, source, RepoConfig)


def _remove_unknown_configuration_keys(data: object, source: Path) -> object:
    if not isinstance(data, Mapping):
        return data
    settings = cast(Mapping[str, object], data)
    top_level_unknown = sorted(set(settings) - RepoConfig.model_fields.keys())
    cleaned = {key: value for key, value in settings.items() if key not in top_level_unknown}
    context_unknown: list[str] = []
    contexts = settings.get("contexts")
    if isinstance(contexts, Mapping):
        context_tables = cast(Mapping[str, object], contexts)
        cleaned_contexts: dict[str, object] = dict(context_tables)
        for context_name, context_value in context_tables.items():
            if not isinstance(context_value, Mapping):
                continue
            context = cast(Mapping[str, object], context_value)
            unknown = sorted(set(context) - ContextConfig.model_fields.keys())
            if unknown:
                context_unknown.extend(f"contexts.{context_name}.{key}" for key in unknown)
                cleaned_contexts[context_name] = {
                    key: value for key, value in context.items() if key not in unknown
                }
        cleaned["contexts"] = cleaned_contexts
    names = [*top_level_unknown, *sorted(context_unknown)]
    if names and source not in _WARNED_UNKNOWN_KEYS:
        print(
            f"{source}: ignoring unknown configuration key(s) {', '.join(names)}; "
            "check the spelling or upgrade Chitty",
            file=sys.stderr,
        )
        _WARNED_UNKNOWN_KEYS.add(source)
    return cleaned


def configured_workflow(start: Path) -> str | None:
    """Return the configured workflow, or None when no repository is found."""
    root = search_root(start)
    return None if root is None else load_repo_config(root).workflow


def runner_required_message(command: str) -> str:
    return f'chitty {command} needs workflow = "runner" in the Chitty config'


def require_runner(config: RepoConfig, command: str) -> None:
    """Reject runner-only commands for repositories using the tickets workflow."""
    if config.workflow != "runner":
        raise ChittyError(runner_required_message(command))


def resolve_workflow(workflow: str | None, chitty_version: str | None) -> str:
    """Resolve the workflow; older or unreadable setups retain runner behavior."""
    if workflow is not None:
        return workflow
    if chitty_version is None:
        return "runner"
    try:
        key = version_key(chitty_version)
    except ChittyError:
        return "runner"
    # Treat trailing zero components as equivalent for this compatibility boundary.
    normalized = key
    while normalized and normalized[-1] == 0:
        normalized = normalized[:-1]
    boundary = version_key(LAST_RUNNER_DEFAULT_VERSION)
    while boundary and boundary[-1] == 0:
        boundary = boundary[:-1]
    return "runner" if normalized <= boundary else "tickets"


def _version_key(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in value.split("."))
    except ValueError as error:
        raise ChittyError(f"invalid Chitty version {value!r}") from error


def version_key(value: str) -> tuple[int, ...]:
    """Return the numeric components used to compare Chitty versions."""
    return _version_key(value)


def check_setup_version(config: RepoConfig) -> None:
    recorded = config.chitty_version
    if recorded is not None and _version_key(recorded) > _version_key(CHITTY_VERSION):
        raise ChittyError(f"repository needs Chitty {recorded} or later")


def config_source(root: Path) -> Path | None:
    """Return the repository file containing Chitty configuration."""
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


def chitty_data_path() -> Path:
    """Machine-local directory for Chitty data."""
    base = Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser()
    return base / "chitty"


def inbox_path(project: str) -> Path:
    """Machine-local inbox directory for a registered project."""
    return chitty_data_path() / "inbox" / project


def usage_path(project: str) -> Path:
    """Machine-local usage history file for a registered project name."""
    base = Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser()
    return base / "chitty" / "usage" / f"{project}.jsonl"


def registered_projects() -> list[str]:
    base = inbox_path("_").parent
    return sorted(path.name for path in base.iterdir() if path.is_dir()) if base.exists() else []


def register_project(project: str, root: Path | None) -> Path:
    """Claim a project inbox name, refusing ownership by another repository."""
    directory = inbox_path(project)
    owner = directory / "repo"
    resolved = str(root.resolve()) if root is not None else ""
    current = owner.read_text().strip() if owner.exists() else ""
    if current and root is not None and not Path(current).is_dir():
        print(
            f"warning: project {project} was registered to {current}, which no longer exists; "
            f"registered {resolved} instead",
            file=sys.stderr,
        )
        current = ""
    if current and current != resolved and not _same_git_repository(Path(current), root):
        raise ChittyError(
            f"project {project!r} is registered to {current}; choose explicit project = name"
        )
    directory.mkdir(parents=True, exist_ok=True)
    if resolved and not current:
        owner.write_text(resolved + "\n")
    elif not owner.exists():
        owner.write_text("")
    return directory


def _same_git_repository(owner: Path, root: Path | None) -> bool:
    """Whether two checkouts share Git's common directory.

    Keep the first registered checkout as the inbox owner: worktrees are the
    same repository, but recording their transient path would break that link.
    """
    if root is None:
        return False
    owner_git_dir = git_common_dir(owner)
    root_git_dir = git_common_dir(root)
    return owner_git_dir is not None and owner_git_dir == root_git_dir


@cache
def git_common_dir(root: Path) -> Path | None:
    if not git.is_repository(root):
        return None
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        command = "git rev-parse --git-common-dir"
        raise ChittyError(f"`{command}` failed in {root}:\n{result.stderr.strip()}")
    common_dir = Path(result.stdout.strip())
    return (root / common_dir).resolve() if not common_dir.is_absolute() else common_dir.resolve()


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
