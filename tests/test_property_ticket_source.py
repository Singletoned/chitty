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
    changed: bool | Callable[[str], bool],
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
        changed if callable(changed) else lambda ref: changed,
    )


class TestTicketSource(unittest.TestCase):
    @given(st.data(), graphs(), task_ids(), st.sampled_from(MAIN_BRANCHES), st.booleans())
    def test_rule_1_provisional_follows_the_other_rules_unless_none_apply(
        self, data, graph, task_id, main_branch, changed
    ):
        maps = data.draw(ref_maps(task_id, graph.commits, graph.commits, data.draw(st.booleans())))
        main_tip = data.draw(st.none() | st.sampled_from(graph.commits))
        current = data.draw(current_branches(task_id, main_branch))

        def outcome(provisional):
            try:
                return (
                    "value",
                    call(
                        task_id,
                        provisional,
                        current,
                        main_branch,
                        main_tip,
                        maps,
                        graph.contains,
                        changed,
                    ),
                )
            except ChittyError as error:
                return ("error", str(error))

        ordinary = outcome(False)
        provisional = outcome(True)
        if ordinary == ("value", main_branch) or (
            ordinary[0] == "error" and "has no tip" in ordinary[1]
        ):
            self.assertEqual(provisional, ("value", WORKING_TREE))
        else:
            self.assertEqual(provisional, ordinary)

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

    @given(st.data(), graphs(), task_ids(), st.sampled_from(MAIN_BRANCHES))
    def test_rules_4_and_6_choose_among_generated_candidates(
        self, data, graph, task_id, main_branch
    ):
        branch = str(task_id).lower()
        if graph.arms:
            arm = data.draw(st.sampled_from(graph.arms))
            candidate_line = graph.chain + arm
            other_arm = next(line for line in graph.arms if line != arm)
            main_choices = graph.chain + other_arm + graph.unrelated
        else:
            candidate_line = graph.chain
            main_choices = graph.chain + graph.unrelated
        main_tip = data.draw(st.none() | st.sampled_from(main_choices))
        eligible = tuple(
            commit
            for commit in candidate_line
            if main_tip is None or not graph.contains(main_tip, commit)
        )
        if not eligible:
            main_tip = None
            eligible = candidate_line
        # One to four ticket refs are distributed on the candidate line.
        count = data.draw(st.integers(min_value=1, max_value=4))
        has_local = count == 4 or data.draw(st.booleans())
        refs = [branch] if has_local else []
        remote_names = data.draw(
            st.lists(
                st.sampled_from(("zeta", "alpha", "beta")),
                min_size=count - int(has_local),
                max_size=count - int(has_local),
                unique=True,
            )
        )
        refs.extend(f"{name}/{branch}" for name in remote_names)
        tips = {ref: data.draw(st.sampled_from(eligible)) for ref in refs}
        local_tips = {ref: tip for ref, tip in tips.items() if "/" not in ref}
        remote_tips = {ref: tip for ref, tip in tips.items() if "/" in ref}
        highest = next(commit for commit in reversed(candidate_line) if commit in tips.values())
        # Tie examples are drawn, while untied layouts remain possible.
        if len(refs) >= 2 and data.draw(st.booleans()):
            tied = data.draw(st.sampled_from(tuple(tips)))
            tips[tied] = highest
            other = next(ref for ref in tips if ref != tied)
            tips[other] = highest
        local_tips = {ref: tip for ref, tip in tips.items() if "/" not in ref}
        remote_tips = {ref: tip for ref, tip in tips.items() if "/" in ref}
        # Add dropped candidates at/below main and decoys without affecting selection.
        if main_tip is not None:
            remote_tips["drop/" + branch] = main_tip
        local_decoys, remote_decoys = decoy_names(task_id)
        local_tips[local_decoys[0]] = graph.commits[0]
        remote_tips[remote_decoys[0]] = graph.commits[0]
        matching = [ref for ref, tip in tips.items() if tip == highest]
        chosen = (
            branch
            if branch in matching
            else min(matching, key=lambda ref: (ref.split("/", 1)[0], ref))
        )
        current = data.draw(st.sampled_from((branch, main_branch, local_decoys[0], None)))
        # Force remote-ahead of a checked-out local in generated examples.
        if graph.arms:
            ahead_line = graph.chain + graph.arms[0]
        else:
            ahead_line = graph.chain
        if len(ahead_line) >= 2 and data.draw(st.booleans()):
            local_tips[branch] = ahead_line[-2]
            remote_tips = {"origin/" + branch: ahead_line[-1]}
            main_tip = None
            current = branch
            chosen = "origin/" + branch
            highest = ahead_line[-1]
        result = WORKING_TREE if current == branch and local_tips.get(branch) == highest else chosen
        args = (
            task_id,
            False,
            current,
            main_branch,
            main_tip,
            (local_tips, remote_tips),
            graph.contains,
        )
        self.assertEqual(call(*args, False), result)
        changed_ref = chosen
        with self.assertRaises(ChittyError) as raised:
            call(*args, lambda ref: ref == changed_ref)
        for name in (str(task_id), changed_ref, main_branch):
            self.assertIn(f"`{name}`", str(raised.exception))
        candidate_refs = set(args[5][0]) | set(args[5][1])
        other = next(ref for ref in candidate_refs if ref != chosen)
        unchanged_result = call(*args, lambda ref: ref == other)
        self.assertEqual(unchanged_result, result)

    @given(st.data(), graphs().filter(lambda graph: bool(graph.arms)), task_ids())
    def test_rule_5_divergence_names_generated_remaining_candidates(self, data, graph, task_id):
        branch = str(task_id).lower()
        main_tip = data.draw(st.none() | st.sampled_from(graph.chain))
        arm_tips = tuple(data.draw(st.sampled_from(arm)) for arm in graph.arms)
        local_tips = {branch: arm_tips[0]}
        remote_tips = {f"origin/{branch}": arm_tips[1]}
        dropped_name = f"backup/{branch}"
        if main_tip is not None and data.draw(st.booleans()):
            remote_tips[dropped_name] = main_tip

        with self.assertRaises(ChittyError) as raised:
            call(
                task_id,
                False,
                None,
                "main",
                main_tip,
                (local_tips, remote_tips),
                graph.contains,
                False,
            )
        message = str(raised.exception)
        self.assertIn(f"`{branch}`", message)
        self.assertIn(f"`origin/{branch}`", message)
        if dropped_name in remote_tips:
            self.assertNotIn(f"`{dropped_name}`", message)

    @given(st.data(), graphs(), task_ids(), st.sampled_from(MAIN_BRANCHES))
    def test_decoys_and_unrelated_refs_do_not_change_generated_result(
        self, data, graph, task_id, main_branch
    ):
        candidate_maps = data.draw(
            ref_maps(task_id, graph.commits, graph.commits, data.draw(st.booleans()))
        )
        extra_maps = data.draw(ref_maps(task_id, graph.commits, graph.commits, False))
        local_tips = dict(candidate_maps[0])
        remote_tips = dict(candidate_maps[1])
        expanded_local = local_tips | extra_maps[0]
        expanded_remote = remote_tips | extra_maps[1]
        current = data.draw(current_branches(task_id, main_branch))
        main_tip = data.draw(st.none() | st.sampled_from(graph.commits))
        refs = tuple(expanded_local) + tuple(expanded_remote)
        changed = frozenset(data.draw(st.sets(st.sampled_from(refs)))) if refs else frozenset()
        provisional = data.draw(st.booleans())

        def outcome(maps):
            try:
                return (
                    "value",
                    call(
                        task_id,
                        provisional,
                        current,
                        main_branch,
                        main_tip,
                        maps,
                        graph.contains,
                        lambda ref: ref in changed,
                    ),
                )
            except ChittyError as error:
                return ("error", str(error))

        self.assertEqual(
            outcome((expanded_local, expanded_remote)), outcome((local_tips, remote_tips))
        )
