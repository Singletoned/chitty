import subprocess

from tests.test_review_merge import ReviewMergeTestCase


class TestWorkRebases(ReviewMergeTestCase):
    def setUp(self):
        super().setUp()
        (self.tmp / "setup.py").write_text(
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "Path(sys.argv[1]).write_text(\n"
            "    subprocess.check_output(['git', 'log', '--format=%s'], text=True))\n"
        )

    def prepare_branch(self, status):
        self.git("switch", "--quiet", "-c", "task-1")
        if status == "doing":
            self.run_cli("edit", "1", "-s", "doing")
        self.git("switch", "--quiet", "main")
        self.move_main()

    def test_doing_rebases_before_setup(self):
        self.prepare_branch("doing")
        self.run_cli("run", "--mode", "work")
        self.assertIn("main moved", (self.logs / "setup").read_text())
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", "main", "task-1"],
            cwd=self.root,
            check=True,
        )

    def test_todo_does_not_rebase_before_setup(self):
        self.prepare_branch("todo")
        self.run_cli("run", "--mode", "work")
        self.assertNotIn("main moved", (self.logs / "setup").read_text())
