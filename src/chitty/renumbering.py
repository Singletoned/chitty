"""Pure planning and rewriting for provisional task IDs."""

import re
from collections.abc import Mapping, Sequence

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.model import ACCEPTANCE_CRITERIA, HISTORY, SECTION_ORDER, Task


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


def rewrite_task(task: Task, mapping: Mapping[TaskId, TaskId]) -> Task:
    result = task
    title = replace_ids(task.frontmatter.title, mapping)
    if title != task.frontmatter.title:
        result = result.with_field("title", title)
    parent = task.frontmatter.parent
    if parent is not None:
        rewritten_parent = replace_ids(parent, mapping)
        if rewritten_parent != parent:
            result = result.with_field("parent", rewritten_parent)
    dependencies = [replace_ids(value, mapping) for value in task.frontmatter.depends_on]
    if dependencies != task.frontmatter.depends_on:
        result = result.with_field("depends_on", dependencies)
    for name in SECTION_ORDER:
        if name in (HISTORY, ACCEPTANCE_CRITERIA):
            continue
        text = task.section(name)
        if text is not None:
            rewritten = replace_ids(text, mapping)
            if rewritten != text:
                result = result.with_section(name, rewritten)
    for index, criterion in enumerate(task.criteria, 1):
        rewritten = replace_ids(criterion.text, mapping)
        if rewritten != criterion.text:
            result = result.with_criterion_text(index, rewritten)
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
