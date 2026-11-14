import os
import shutil
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.store import init_repo
from tests.support import CONFIG, RepoTestCase


class TestInitPiIsolation(RepoTestCase):
    def setUp(self):
        super().setUp()
        self.agent = Path(os.environ["HOME"]) / ".pi" / "agent"

    @settings(deadline=None)
    @given(
        extension=st.one_of(st.none(), st.binary(max_size=80)),
        state=st.one_of(st.none(), st.binary(max_size=80)),
        settings=st.one_of(st.none(), st.binary(max_size=160)),
        existing=st.booleans(),
        repeat=st.integers(min_value=1, max_value=3),
    )
    def test_repeated_init_leaves_pi_files_byte_identical(
        self, extension, state, settings, existing, repeat
    ):
        for path in (self.root / "chitty.toml", self.root / "AGENTS.md", self.root / ".gitignore"):
            path.unlink(missing_ok=True)
        shutil.rmtree(self.root / "chitty", ignore_errors=True)
        if existing:
            (self.root / "chitty.toml").write_text(CONFIG)
        shutil.rmtree(self.agent, ignore_errors=True)
        paths = {
            self.agent / "extensions" / "chitty.ts": extension,
            self.agent / "chitty-extension.sha256": state,
            self.agent / "settings.json": settings,
        }
        for path, content in paths.items():
            if content is not None:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        before = {path: path.read_bytes() for path in paths if path.exists()}
        for _ in range(repeat):
            init_repo(self.root, False)
        after = {path: path.read_bytes() for path in paths if path.exists()}
        self.assertEqual(after, before)
