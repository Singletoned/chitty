import shutil
import subprocess

from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestDiscoveredContexts(CliTestCase):
    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace('\n[contexts.human]\nprefix = "HUMAN"\n', "\n")
        )
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "setup")

    def git(self, *args):
        subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def commit_file(self, path, content="---\ntitle: x\nstatus: todo\ncreated: 2026-11-11\n---\n"):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        self.git("add", path)
        self.git("commit", "--quiet", "-m", "ticket")

    def names(self):
        return {context.name for context in Repo.open(self.root).discovered_contexts()}

    def test_main_tip_directory(self):
        self.commit_file("chitty/other/TASK-3--x.md")
        shutil.rmtree(self.root / "chitty/other")
        self.assertEqual(self.names(), {"tasks", "other"})

    def test_ticket_branch_own_file(self):
        self.git("switch", "--quiet", "-c", "task-5")
        self.commit_file("chitty/fifth/TASK-5--x.md")
        self.git("switch", "--quiet", "main")
        self.assertEqual(self.names(), {"tasks", "fifth"})

    def test_ticket_branch_other_file(self):
        self.git("switch", "--quiet", "-c", "task-6")
        self.commit_file("chitty/sixth/TASK-9--y.md")
        self.git("switch", "--quiet", "main")
        self.assertEqual(self.names(), {"tasks"})

    def test_unrelated_branch(self):
        self.git("switch", "--quiet", "-c", "feature")
        self.commit_file("chitty/feat/TASK-7--z.md")
        self.git("switch", "--quiet", "main")
        self.assertEqual(self.names(), {"tasks"})

    def test_does_not_read_history_or_parse_tickets(self):
        self.commit_file("chitty/tasks/TASK-1--x.md")
        self.git("switch", "--quiet", "-c", "task-1")
        self.commit_file("chitty/tasks/TASK-1--x.md", "branch edit")
        self.git("switch", "--quiet", "main")
        self.commit_file("chitty/tasks/TASK-1--x.md", "main edit")
        self.commit_file("chitty/tasks/TASK-2--x.md", "malformed")
        self.commit_file("chitty/other/TASK-3--x.md")
        self.assertEqual(self.names(), {"tasks", "other"})
