from pathlib import Path


def write_refusal(
    task_id: str,
    newer_ref: str,
    newer_sha: str,
    main_branch: str,
    local_branch: bool,
    worktree: Path | None,
    main_checkout: Path,
    checkout_is_main: bool,
    local_behind: bool,
) -> str:
    if newer_ref == main_branch:
        action = (
            f"switch this checkout to {main_branch} first"
            if checkout_is_main
            else f"edit it in the main checkout {main_checkout}"
        )
    elif local_branch:
        action = (
            f"edit it in worktree {worktree}"
            if worktree is not None
            else f"run git switch {newer_ref} first"
        )
    elif local_behind:
        action = f"fast-forward {newer_ref.split('/', 1)[1]} to {newer_ref} first"
    else:
        action = f"run git switch --track {newer_ref} first"
    return f"{task_id} has a newer copy on {newer_ref} ({newer_sha[:10]}); {action}"
