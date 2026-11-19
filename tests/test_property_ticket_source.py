import string
import unittest
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.ticket_source import WORKING_TREE, ticket_source

MAIN_BRANCHES = ("main", "trunk")
UNRELATED_COMMITS = ("u0", "u1", "u2")
MAX_CHAIN = 6
MAX_SHARED = 3
MAX_ARM = 3
MAX_REMOTES = 3


@dataclass(frozen=True)
class Graph:
    """A commit graph whose ancestry is known by construction.

    `ancestors[c]` is every commit `c` contains, `c` included. A chain has
    `chain` `c0`..`cn` and no `arms`; a fork has the shared chain in `chain`
    and two `arms`, each in order. `unrelated` commits contain only themselves.
    """

    commits: tuple[str, ...]
    ancestors: Mapping[str, frozenset[str]]
    chain: tuple[str, ...]
    arms: tuple[tuple[str, ...], ...]
    unrelated: tuple[str, ...]

    def contains(self, a: str, b: str) -> bool:
        return b in self.ancestors[a]


def _line(names: tuple[str, ...], below: frozenset[str]) -> dict[str, frozenset[str]]:
    ancestors = {}
    seen = set(below)
    for name in names:
        seen.add(name)
        ancestors[name] = frozenset(seen)
    return ancestors


@st.composite
def graphs(draw) -> Graph:
    """Draw a chain or a fork, plus up to three unrelated commits."""
    unrelated = UNRELATED_COMMITS[
        : draw(st.integers(min_value=0, max_value=len(UNRELATED_COMMITS)))
    ]
    if draw(st.booleans()):
        chain = tuple(
            f"c{i}" for i in range(draw(st.integers(min_value=1, max_value=MAX_CHAIN)) + 1)
        )
        arms: tuple[tuple[str, ...], ...] = ()
    else:
        chain = tuple(
            f"c{i}" for i in range(draw(st.integers(min_value=0, max_value=MAX_SHARED)) + 1)
        )
        arms = tuple(
            tuple(
                f"{arm}{i}" for i in range(1, draw(st.integers(min_value=1, max_value=MAX_ARM)) + 1)
            )
            for arm in ("a", "b")
        )
    ancestors = _line(chain, frozenset())
    for arm in arms:
        ancestors.update(_line(arm, ancestors[chain[-1]]))
    ancestors.update({name: frozenset({name}) for name in unrelated})
    commits = chain + tuple(name for arm in arms for name in arm) + unrelated
    return Graph(commits, ancestors, chain, arms, unrelated)


@st.composite
def task_ids(draw) -> TaskId:
    prefix = draw(st.text(alphabet=string.ascii_uppercase, min_size=1, max_size=5))
    return TaskId(prefix, draw(st.integers(min_value=1, max_value=99)))


def decoy_names(task_id: TaskId) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Local and remote names that look like the ticket's but never match it."""
    branch = str(task_id).lower()
    local = (f"{branch}0", f"feature/{branch}", str(task_id), "other")
    remote = (f"origin/{branch}0", f"origin/x/{branch}", branch, "origin/other")
    return local, remote


@st.composite
def ref_maps(
    draw,
    task_id: TaskId,
    candidate_commits: tuple[str, ...],
    decoy_commits: tuple[str, ...],
    with_candidates: bool,
) -> tuple[dict[str, str], dict[str, str]]:
    """Draw `(local_tips, remote_tips)`.

    With `with_candidates`, at least one candidate (the local ticket branch
    and remote `<remote>/<branch>` names), each at a commit from
    `candidate_commits`. Decoy and unrelated names, at commits from
    `decoy_commits`, are drawn either way.
    """
    branch = str(task_id).lower()
    local: dict[str, str] = {}
    remote: dict[str, str] = {}
    if with_candidates:
        has_local = draw(st.booleans())
        if has_local:
            local[branch] = draw(st.sampled_from(candidate_commits))
        remotes = draw(
            st.lists(
                st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=5),
                min_size=0 if has_local else 1,
                max_size=MAX_REMOTES,
                unique=True,
            )
        )
        for name in remotes:
            remote[f"{name}/{branch}"] = draw(st.sampled_from(candidate_commits))
    local_decoys, remote_decoys = decoy_names(task_id)
    for names, tips in ((local_decoys, local), (remote_decoys, remote)):
        for name in draw(st.lists(st.sampled_from(names), unique=True)):
            tips[name] = draw(st.sampled_from(decoy_commits))
    return local, remote


def current_branches(task_id: TaskId, main_branch: str):
    """A candidate name (present in `local_tips` or not), a decoy, main or detached."""
    branch = str(task_id).lower()
    return st.sampled_from((branch, f"{branch}0", f"feature/{branch}", main_branch, None))


def call(
    task_id: TaskId,
    provisional: bool,
    current_branch: str | None,
    main_branch: str,
    main_tip: str | None,
    maps: tuple[dict[str, str], dict[str, str]],
    contains: Callable[[str, str], bool],
    changed: bool,
) -> str:
    local_tips, remote_tips = maps
    return ticket_source(
        task_id,
        provisional,
        current_branch,
        main_branch,
        main_tip,
        local_tips,
        remote_tips,
        contains,
        lambda ref: changed,
    )


@st.composite
def legacy_graphs(draw):
    """Digit commits for the fixed examples `TASK-403` and `TASK-404` replace."""
    fork = draw(st.booleans())

    def contains(a, b):
        a, b = int(a), int(b)
        if a == b:
            return True
        if not fork:
            return a > b
        # 0 is the shared root; 1 and 2 fork; 3+ are unrelated commits.
        return a in (1, 2) and b == 0

    return fork, contains


class TestTicketSource(unittest.TestCase):
    @given(st.data(), graphs(), task_ids(), st.sampled_from(MAIN_BRANCHES), st.booleans())
    def test_rule_1_provisional_reads_the_working_tree(
        self, data, graph, task_id, main_branch, changed
    ):
        maps = data.draw(ref_maps(task_id, graph.commits, graph.commits, data.draw(st.booleans())))
        main_tip = data.draw(st.none() | st.sampled_from(graph.commits))
        current = data.draw(current_branches(task_id, main_branch))
        result = call(task_id, True, current, main_branch, main_tip, maps, graph.contains, changed)
        self.assertEqual(result, WORKING_TREE)

    @given(st.data(), graphs(), task_ids(), st.sampled_from(MAIN_BRANCHES), st.booleans())
    def test_rules_2_and_3_candidates_main_contains_are_dropped(
        self, data, graph, task_id, main_branch, changed
    ):
        main_tip = data.draw(st.sampled_from(graph.commits))
        behind = tuple(sorted(graph.ancestors[main_tip]))
        maps = data.draw(ref_maps(task_id, behind, graph.commits, True))
        current = data.draw(current_branches(task_id, main_branch))
        result = call(task_id, False, current, main_branch, main_tip, maps, graph.contains, changed)
        self.assertEqual(result, WORKING_TREE if current == main_branch else main_branch)

    @given(st.data(), graphs(), task_ids(), st.sampled_from(MAIN_BRANCHES), st.booleans())
    def test_rule_3_no_candidates_reads_main(self, data, graph, task_id, main_branch, changed):
        maps = data.draw(ref_maps(task_id, graph.commits, graph.commits, False))
        main_tip = data.draw(st.none() | st.sampled_from(graph.commits))
        current = data.draw(current_branches(task_id, main_branch))

        def result():
            return call(
                task_id, False, current, main_branch, main_tip, maps, graph.contains, changed
            )

        if current == main_branch:
            self.assertEqual(result(), WORKING_TREE)
        elif main_tip is None:
            with self.assertRaisesRegex(ChittyError, f"`{main_branch}`"):
                result()
        else:
            self.assertEqual(result(), main_branch)

    @given(legacy_graphs(), task_ids(), st.booleans())
    def test_candidate_at_chosen_tip_and_local_checkout(self, graph, task_id, fork):
        is_fork, contains = graph
        branch = str(task_id).lower()
        # main is unrelated to the candidate chain on a fork, and older on
        # a linear history.
        ancestor, descendant, main_tip = ("0", "1", "3") if is_fork else ("1", "2", "0")
        result = ticket_source(
            task_id,
            False,
            branch,
            "main",
            main_tip,
            {branch: descendant},
            {"origin/" + branch: ancestor},
            contains,
            lambda ref: False,
        )
        # In chain, local is the descendant; in fork neither candidate is
        # dropped and the root/arm relationship still chooses the descendant.
        self.assertEqual(result, WORKING_TREE)

    @given(legacy_graphs(), task_ids(), st.booleans())
    def test_equal_tip_prefers_local_then_remote_name(self, graph, task_id, current):
        _, contains = graph
        branch = str(task_id).lower()
        tips = {branch: "2"} if current else {}
        result = ticket_source(
            task_id,
            False,
            branch if current else None,
            "main",
            "0",
            tips,
            {"zeta/" + branch: "2", "alpha/" + branch: "2"},
            contains,
            lambda ref: False,
        )
        self.assertEqual(result, WORKING_TREE if current else "alpha/" + branch)

    @given(legacy_graphs(), task_ids())
    def test_changed_on_both_reports_chosen_remote(self, graph, task_id):
        _, contains = graph
        branch = str(task_id).lower()
        with self.assertRaises(ChittyError) as raised:
            ticket_source(
                task_id,
                False,
                None,
                "main",
                "0",
                {},
                {"origin/" + branch: "2"},
                contains,
                lambda ref: ref == "origin/" + branch,
            )
        message = str(raised.exception)
        for name in (str(task_id), "origin/" + branch, "main"):
            self.assertIn(f"`{name}`", message)

    @given(task_ids())
    def test_divergence_names_remaining_candidates_not_dropped_ones(self, task_id):
        def contains(a, b):
            return a == b or (a in ("1", "2") and b == "0")

        branch = str(task_id).lower()
        with self.assertRaises(ChittyError) as raised:
            ticket_source(
                task_id,
                False,
                None,
                "main",
                "1",
                {branch: "1"},
                {"origin/" + branch: "2", "backup/" + branch: "3"},
                contains,
                lambda ref: False,
            )
        message = str(raised.exception)
        self.assertIn(f"`origin/{branch}`", message)
        self.assertIn(f"`backup/{branch}`", message)
        self.assertNotIn(f"`{branch}`", message)

    @given(legacy_graphs(), task_ids())
    def test_decoys_and_unrelated_refs_do_not_change_result(self, graph, task_id):
        _, contains = graph
        branch = str(task_id).lower()
        base = ticket_source(
            task_id,
            False,
            None,
            "main",
            "0",
            {branch: "2"},
            {},
            contains,
            lambda ref: False,
        )
        expanded = ticket_source(
            task_id,
            False,
            None,
            "main",
            "0",
            {
                branch: "2",
                branch.upper(): "3",
                branch + "0": "3",
                "feature/" + branch: "3",
                "other": "3",
            },
            {"origin/" + branch + "0": "3", "origin/x/" + branch: "3"},
            contains,
            lambda ref: False,
        )
        self.assertEqual(expanded, base)
