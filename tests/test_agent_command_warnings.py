import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.config import agent_command_warnings

COMMANDS = st.one_of(
    st.text(),
    st.tuples(st.text(), st.text()).map(lambda parts: parts[0] + "{prompt}" + parts[1]),
    st.sampled_from(["", " ", "\t\n"]),
)


class TestAgentCommandWarnings(unittest.TestCase):
    @given(
        st.one_of(st.none(), COMMANDS),
        st.dictionaries(st.from_regex(r"[a-z]{1,8}", fullmatch=True), COMMANDS, max_size=4),
    )
    def test_warns_for_each_nonblank_command_without_prompt(self, command, commands):
        expected = []
        if command is not None and command.strip() and "{prompt}" not in command:
            expected.append("agent_command")
        expected.extend(
            f"agent_commands.{name}"
            for name, value in sorted(commands.items())
            if value.strip() and "{prompt}" not in value
        )
        warnings = agent_command_warnings(command, commands)
        self.assertEqual(len(warnings), len(expected))
        for warning, setting in zip(warnings, expected, strict=True):
            self.assertTrue(warning.startswith(f"{setting} has no {{prompt}}"), warning)
