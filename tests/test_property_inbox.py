import os
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.config import inbox_path, load_repo_config, register_project
from chitty.errors import ChittyError
from chitty.inbox import pull, suggest
from chitty.store import BACKLOG_DESCRIPTION, Repo
from tests.support import RepoTestCase

EXAMPLES = 50
PROJECT_LINE = 'default_context = "tasks"\nproject = "target"'

TITLE_SPECIALS = st.sampled_from(["\u2028", "\u2029", "\x84", "\x85", "-", "--", "---"])
CHARACTERS = st.characters(blacklist_characters="\r\n", blacklist_categories=("Cs",))
TITLES = st.lists(st.one_of(CHARACTERS, TITLE_SPECIALS), max_size=12).map("".join)


def _safe_description_line(line: str) -> bool:
    return not (line.lstrip().startswith(("## ", "```", "~~~")) or "\f" in line)


DESCRIPTION_LINES = st.one_of(
    st.lists(st.one_of(CHARACTERS, st.sampled_from(["\u2028", "-", " ", "\t"])), max_size=40)
    .map("".join)
    .filter(_safe_description_line),
    st.just("---"),
)
DESCRIPTIONS = st.one_of(st.none(), st.lists(DESCRIPTION_LINES, max_size=6).map("\n".join))


def _expected_description(description: str | None) -> str:
    text = (description or "").strip()
    if not text:
        return BACKLOG_DESCRIPTION
    return "\n".join(line.rstrip() for line in text.split("\n"))


class TestInboxProperties(RepoTestCase):
    def setUp(self):
        super().setUp()
        self._actor = mock.patch.dict(os.environ, {"CHITTY_ACTOR": "test-agent"})
        self._actor.start()
        self.addCleanup(self._actor.stop)
        config = (self.root / "chitty.toml").read_text()
        (self.root / "chitty.toml").write_text(
            config.replace('default_context = "tasks"', PROJECT_LINE)
        )
        register_project("target", self.root)
        self.repo = Repo(self.root, load_repo_config(self.root))

    def _suggestion_files(self):
        return sorted(inbox_path("target").glob("suggestion-*.md"))

    @settings(max_examples=EXAMPLES, deadline=None)
    @given(title=TITLES, description=DESCRIPTIONS)
    def test_accepted_suggestion_pulls_with_the_same_title_and_description(
        self, title, description
    ):
        before = len(self._suggestion_files())
        try:
            suggest("target", title, description, True, self.root)
        except ChittyError:
            self.assertEqual(len(self._suggestion_files()), before)
            return

        self.assertEqual(len(self._suggestion_files()), before + 1)
        task_ids = pull(self.repo)
        self.assertEqual(len(task_ids), 1)
        self.assertEqual(len(self._suggestion_files()), 0)
        task = self.repo.find(self.repo.resolve(task_ids[0])).task
        self.assertEqual(task.frontmatter.title, title)
        self.assertEqual(task.section("Description"), _expected_description(description))
