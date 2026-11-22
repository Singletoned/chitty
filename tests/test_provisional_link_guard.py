from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo
from tests.test_provisional_preflight import TestProvisionalPreflight


class TestProvisionalLinkGuard(TestProvisionalPreflight):
    def fixture(self, stale, link):
        self.init_git()
        self.file("tasks", "TASK-AAAAAA", provisional=True)
        if not stale:
            self.file("tasks", "TASK-BAAAAA", provisional=True)
        location, name = ("tasks", "TASK-3") if stale else ("other", "OTHER-1")
        path = self.file(location, name)
        text = path.read_text()
        if link == "structured":
            field = "parent: task-aaaaaa" if stale else "depends_on: [TASK-BAAAAA]"
            text = text.replace("status: todo\n", f"status: todo\n{field}\n")
        elif link == "prose":
            text += "See TASK-AAAAAA.\n" if stale else "See TASK-BAAAAA.\n"
        else:
            text = text.replace("status: todo\n", "status: todo\ndepends_on: [TASK-CAAAAA]\n")
        path.write_text(text)
        self.commit()
        if stale:
            self.git("switch", "-c", "task-3")
            path.write_text(
                path.read_text()
                .replace("parent: task-aaaaaa\n", "")
                .replace("See TASK-AAAAAA.\n", "")
            )
            if link != "structured" and link != "prose":
                path.write_text(path.read_text() + "\nBranch.\n")
            self.commit()
            self.git("switch", "main")
            self.assertEqual(Repo.open(self.root).source_of(TaskId.parse("TASK-3")), "task-3")
        return path

    def state(self):
        return (
            self.git("rev-parse", "HEAD"),
            self.git("ls-files", "-s"),
            {p: p.read_bytes() for p in (self.root / "chitty").rglob("*") if p.is_file()},
        )

    def test_links(self):
        for stale in (False, True):
            with self.subTest(stale=stale):
                # Each fixture needs its own repository.
                if stale:
                    continue
                self.check_refusal(stale)

    def test_stale_link(self):
        self.check_refusal(True)

    def check_refusal(self, stale):
        self.fixture(stale, "structured")
        before = self.state()
        expected = (
            "cannot renumber TASK-AAAAAA: TASK-3 links to it in parent"
            if stale
            else "cannot renumber TASK-BAAAAA: OTHER-1 links to it in depends_on"
        )
        with self.assertRaises(ChittyError) as error:
            Repo.open(self.root)._plan_provisional_renumbering()
        self.assertEqual(str(error.exception), expected)
        self.assertEqual(self.state(), before)

    def check_success(self, stale, link):
        path = self.fixture(stale, link)
        before = self.state()
        mapping, writable = Repo.open(self.root)._plan_provisional_renumbering()
        expected = {"TASK-AAAAAA": "TASK-4" if stale else "TASK-1"}
        if not stale:
            expected["TASK-BAAAAA"] = "TASK-2"
        self.assertEqual({str(k): str(v) for k, v in mapping.items()}, expected)
        self.assertNotIn(path, [t.path for t in writable])
        self.assertEqual(self.state(), before)

    def test_unconfigured_prose(self):
        self.check_success(False, "prose")

    def test_stale_prose(self):
        self.check_success(True, "prose")

    def test_control(self):
        self.check_success(False, "control")
