"""Choose the authoritative source for a ticket."""

from collections.abc import Callable, Mapping

from chitty.errors import ChittyError
from chitty.ids import TaskId

WORKING_TREE = ""


def ticket_source(
    task_id: TaskId,
    provisional: bool,
    current_branch: str | None,
    main_branch: str,
    main_tip: str | None,
    local_tips: Mapping[str, str],
    remote_tips: Mapping[str, str],
    contains: Callable[[str, str], bool],
    changed_on_both: Callable[[str], bool],
) -> str:
    branch_name = str(task_id).lower()
    candidates: dict[str, str] = {}
    if branch_name in local_tips:
        candidates[branch_name] = local_tips[branch_name]
    for ref, tip in remote_tips.items():
        if "/" in ref and ref.split("/", 1)[1] == branch_name:
            candidates[ref] = tip

    if main_tip is not None:
        candidates = {ref: tip for ref, tip in candidates.items() if not contains(main_tip, tip)}
    if not candidates:
        if provisional:
            return WORKING_TREE
        if current_branch == main_branch:
            return WORKING_TREE
        if main_tip is None:
            raise ChittyError(f"configured main branch `{main_branch}` has no tip")
        return main_branch

    chosen_tip = next(
        (
            tip
            for tip in candidates.values()
            if all(contains(tip, other) for other in candidates.values())
        ),
        None,
    )
    if chosen_tip is None:
        names = ", ".join(f"`{ref}`" for ref in sorted(candidates))
        raise ChittyError(f"ticket `{task_id}` has diverged refs: {names}")

    matching = [ref for ref, tip in candidates.items() if tip == chosen_tip]
    local = branch_name if branch_name in matching else None
    if local is not None:
        chosen = local
    else:
        chosen = min(matching, key=lambda ref: (ref.split("/", 1)[0], ref))
    if changed_on_both(chosen):
        raise ChittyError(f"ticket `{task_id}` changed on both `{chosen}` and `{main_branch}`")
    if current_branch == branch_name and local_tips.get(branch_name) == chosen_tip:
        return WORKING_TREE
    return chosen
