"""Pure planning and rewriting for provisional task IDs."""

import re
from collections.abc import Mapping, Sequence

from chitty.errors import ChittyError
from chitty.ids import TaskId


def plan_renumbering(
    used: Mapping[str, set[int]], provisional: Sequence[TaskId]
) -> dict[TaskId, TaskId]:
    seen: set[TaskId] = set()
    for task_id in provisional:
        if task_id in seen:
            raise ChittyError(f"duplicate provisional task ID {task_id}")
        seen.add(task_id)
        if isinstance(task_id.number, int):
            raise ChittyError(f"task ID {task_id} is not provisional")

    result: dict[TaskId, TaskId] = {}
    by_prefix: dict[str, list[TaskId]] = {}
    for task_id in provisional:
        by_prefix.setdefault(task_id.prefix, []).append(task_id)
    for prefix, task_ids in by_prefix.items():
        number = max(used.get(prefix, set()), default=0)
        for task_id in sorted(task_ids):
            number += 1
            result[task_id] = TaskId(prefix, number)
    return result


def replace_ids(text: str, mapping: Mapping[TaskId, TaskId]) -> str:
    if not mapping:
        return text
    replacements = {str(old): str(new) for old, new in mapping.items()}
    alternatives = "|".join(
        re.escape(task_id) for task_id in sorted(replacements, key=len, reverse=True)
    )
    pattern = re.compile(rf"(?<![A-Za-z0-9-])(?:{alternatives})(?![A-Za-z0-9])")
    return pattern.sub(lambda match: replacements[match.group()], text)
