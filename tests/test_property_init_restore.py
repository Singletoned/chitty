import os
import re
import subprocess
import tempfile
import tomllib
from pathlib import Path
from unittest import mock

from click.testing import CliRunner
from hypothesis import example, given, settings
from hypothesis import strategies as st

from chitty import config
from chitty.cli import cli
from chitty.store import ChittyError, _default_project, managed_block
from tests import examples
from tests.support import RepoTestCase


def git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def snapshot(root):
    files = {}
    for name in ("chitty.toml", "AGENTS.md", "CLAUDE.md", ".gitignore"):
        path = root / name
        files[name] = (
            ("link", os.readlink(path))
            if path.is_symlink()
            else (("file", path.read_bytes()) if path.exists() else None)
        )
    directories = set()
    if (root / "chitty").is_dir():
        for directory, _, _ in os.walk(root / "chitty"):
            directories.add(str(Path(directory).relative_to(root)))
    return (
        git(root, "rev-parse", "HEAD"),
        git(root, "status", "--porcelain", "--untracked-files=all"),
        files,
        directories,
    )


class TestInitRestore(RepoTestCase):
    def repository(self):
        root = Path(tempfile.mkdtemp(dir=self.tmp))
        git(root, "init")
        git(root, "config", "user.name", "Test")
        git(root, "config", "user.email", "test@example.com")
        git(root, "commit", "--allow-empty", "-m", "baseline")
        return root

    def stale(self, root, agents_removed, ignore_removed, extra_present):
        result = CliRunner().invoke(cli, ["init", "--autocommit"])
        self.assertEqual(result.exit_code, 0, result.output)
        path = root / "chitty.toml"
        text = re.sub(r'chitty_version = "[^"]+"', 'chitty_version = "0.1.0"', path.read_text())
        path.write_text(text + '\n[contexts.extra]\nprefix = "EXTRA"\n')
        agents = root / "AGENTS.md"
        if agents_removed:
            agents.unlink()
        else:
            text = agents.read_text()
            block = managed_block(text)
            assert block is not None
            agents.write_text(text.replace(block, ""))
        ignore = root / ".gitignore"
        if ignore_removed:
            ignore.unlink()
        else:
            ignore.write_text(ignore.read_text().replace(".worktrees/\n", ""))
        (root / "CLAUDE.md").unlink()
        if extra_present:
            (root / "chitty" / "extra").mkdir(parents=True)
        git(root, "add", "-A")
        git(root, "commit", "-m", "stale setup")
        return tomllib.loads(path.read_text())["project"]

    @settings(max_examples=examples(30), deadline=None)
    @example(
        case=("stale", "registration"),
        agents_removed=True,
        ignore_removed=True,
        extra_present=False,
    )
    @example(
        case=("fresh", "registration"),
        agents_removed=False,
        ignore_removed=False,
        extra_present=False,
    )
    @example(
        case=("fresh", "hook"), agents_removed=False, ignore_removed=False, extra_present=False
    )
    @example(
        case=("stale", "hook"), agents_removed=False, ignore_removed=False, extra_present=False
    )
    @example(
        case=("refresh", "hook"), agents_removed=False, ignore_removed=False, extra_present=False
    )
    @given(
        case=st.sampled_from(
            (
                ("stale", "registration"),
                ("fresh", "registration"),
                ("fresh", "hook"),
                ("stale", "hook"),
                ("refresh", "hook"),
            )
        ),
        agents_removed=st.booleans(),
        ignore_removed=st.booleans(),
        extra_present=st.booleans(),
    )
    def test_failure_restores_setup(self, case, agents_removed, ignore_removed, extra_present):
        root = self.repository()
        data = tempfile.mkdtemp(dir=self.tmp)
        old = Path.cwd()
        try:
            os.chdir(root)
            with mock.patch.dict(os.environ, {"XDG_DATA_HOME": data, "CHITTY_ACTOR": "tester"}):
                kind, failure = case
                name = (
                    self.stale(root, agents_removed, ignore_removed, extra_present)
                    if kind in ("stale", "refresh")
                    else _default_project(root.name)
                )
                if failure == "registration":
                    other = Path(tempfile.mkdtemp(dir=self.tmp))
                    if kind == "stale":
                        (config.inbox_path(name) / "repo").write_text(str(other.resolve()) + "\n")
                    else:
                        config.register_project(name, other)
                else:
                    hook = root / ".git/hooks/pre-commit"
                    hook.write_text("#!/bin/sh\necho HOOKSTDERR >&2\nexit 1\n")
                    hook.chmod(0o755)
                before = snapshot(root)
                if kind == "refresh":
                    from chitty.store import Repo

                    with self.assertRaises(ChittyError) as error:
                        Repo.open(root).refresh_setup()
                    self.assertIn("HOOKSTDERR", str(error.exception))
                else:
                    args = ["add", "T", "-d", "x"] if kind == "stale" else ["init", "--autocommit"]
                    result = CliRunner().invoke(cli, args)
                    self.assertNotEqual(result.exit_code, 0, result.output)
                    self.assertIn(
                        "is registered to" if failure == "registration" else "HOOKSTDERR",
                        result.output,
                    )
                self.assertEqual(snapshot(root), before)
        finally:
            os.chdir(old)

    def test_successful_fresh_and_stale(self):
        for kind in ("fresh", "stale"):
            root = self.repository()
            data = tempfile.mkdtemp(dir=self.tmp)
            old = Path.cwd()
            try:
                os.chdir(root)
                with mock.patch.dict(os.environ, {"XDG_DATA_HOME": data, "CHITTY_ACTOR": "tester"}):
                    if kind == "stale":
                        self.stale(root, True, True, False)
                        result = CliRunner().invoke(cli, ["add", "T", "-d", "x"])
                        self.assertEqual(result.exit_code, 0, result.output)
                        self.assertEqual(
                            tomllib.loads((root / "chitty.toml").read_text())["chitty_version"],
                            config.CHITTY_VERSION,
                        )
                    else:
                        result = CliRunner().invoke(cli, ["init", "--autocommit"])
                        self.assertEqual(result.exit_code, 0, result.output)
                        self.assertEqual(
                            git(root, "log", "-1", "--format=%s"),
                            "chitty: initialize and enable autocommit",
                        )
                    self.assertEqual(git(root, "status", "--porcelain"), "")
            finally:
                os.chdir(old)
