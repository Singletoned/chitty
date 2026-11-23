from hypothesis import given
from hypothesis import strategies as st

from chitty.run import stalled_agent_message


@given(
    first_line=st.text().filter(lambda s: s.splitlines() in ([], [s])),
    seconds=st.integers(min_value=0),
    returncode=st.integers(),
    output=st.text(),
)
def test_stalled_agent_message(first_line, seconds, returncode, output):
    lines = stalled_agent_message(first_line, seconds, returncode, output).split("\n")
    assert lines[0] == first_line
    assert lines[1] == f"last session: exit {returncode} after {seconds}s"
    assert lines[2:] == (output.splitlines()[-40:] if output else ["(no output)"])
