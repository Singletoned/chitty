#!/usr/bin/env python3
"""List the commands agents ran, as input for a restricted client's allowlist.

Compound shell is split into its individual commands, including pipelines,
substitutions, `bash -c` and wrappers such as `xargs`. Shell run through the
`ctx_*` tools is included. Code in other languages is counted but not parsed.
This is a static parse: variables and generated commands cannot be resolved.
"""

import collections
import json
import pathlib
import re
import shlex
import sys

KEYWORDS = {
    "!", "[[", "]]", "{", "}", "case", "do", "done", "elif", "else", "esac", "fi", "if", "then",
    "until", "while",
}  # fmt: skip
LOOP_HEADERS = {"for", "select"}
SHELLS = {"bash", "sh", "zsh"}
WRAPPERS = {"command", "env", "exec", "nice", "nohup", "sudo", "time", "timeout", "xargs"}
SUBCOMMANDS = {"brew", "chitty", "docker", "gh", "git", "make", "mate", "npm", "npx", "pi", "uv"}
GIT_VALUE_FLAGS = {"-C", "-c"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?(?:\n\s*\2\s*(?=\n|$)|\Z)", re.DOTALL)
REDIRECT = re.compile(r"^\d*[<>]")
SHELL_LANGUAGES = {"bash", "sh", "shell", "zsh"}


def extract_substitutions(script):
    """Return `script` with `$(...)` and backticks replaced, plus their contents."""
    out, found, i, quote = [], [], 0, None
    while i < len(script):
        char = script[i]
        if char == "'" and quote != '"':
            quote = None if quote == "'" else "'"
        elif char == '"' and quote != "'":
            quote = None if quote == '"' else '"'
        elif quote != "'" and script.startswith("$(", i) and not script.startswith("$((", i):
            depth, j = 1, i + 2
            while j < len(script) and depth:
                depth += {"(": 1, ")": -1}.get(script[j], 0)
                j += 1
            found.append(script[i + 2 : j - 1])
            out.append("SUBST")
            i = j
            continue
        elif quote != "'" and char == "`":
            end = script.find("`", i + 1)
            if end != -1:
                found.append(script[i + 1 : end])
                out.append("SUBST")
                i = end + 1
                continue
        out.append(char)
        i += 1
    return "".join(out), found


def segments(script):
    """Split shell into word lists at control operators, dropping redirect targets."""
    lexer = shlex.shlex(script, posix=True, punctuation_chars=";|&()<>")
    lexer.whitespace_split = True
    lexer.whitespace = " \t\r\n"
    current, skip_next = [], False
    for token in lexer:
        if skip_next:
            skip_next = False
        elif token and set(token) <= set("<>"):
            skip_next = True
        elif token and set(token) <= set(";|&()"):
            if current:
                yield current
            current = []
        elif REDIRECT.match(token):
            skip_next = not re.search(r"[<>]&?.", token)
        else:
            current.append(token)
    if current:
        yield current


def executable_key(words):
    head = words[0].rsplit("/", 1)[-1]
    if head not in SUBCOMMANDS:
        return head
    rest, i = words[1:], 0
    while i < len(rest) and rest[i].startswith("-"):
        i += 2 if head == "git" and rest[i] in GIT_VALUE_FLAGS else 1
    if i >= len(rest):
        return head
    if head == "uv" and rest[i] == "run":
        inner = [w for w in rest[i + 1 :] if not w.startswith("-")]
        return f"uv run {inner[0].rsplit('/', 1)[-1]}" if inner else "uv run"
    return f"{head} {rest[i]}"


def commands_in(script):
    """Yield one key per command in a shell script, recursing into nested shell."""
    script = HEREDOC.sub("\n", script)
    script, nested = extract_substitutions(script)
    for inner in nested:
        yield from commands_in(inner)
    for words in segments(script):
        yield from unwrap(words)


def unwrap(words):
    while words and (words[0] in KEYWORDS or ASSIGNMENT.match(words[0])):
        words = words[1:]
    if not words or words[0] in LOOP_HEADERS or words[0] == "SUBST":
        return
    head = words[0].rsplit("/", 1)[-1]
    if head in SHELLS and "-c" in words[:-1]:
        yield from commands_in(words[words.index("-c") + 1])
    elif head in WRAPPERS:
        rest = words[1:]
        while rest and (
            rest[0].startswith("-")
            or ASSIGNMENT.match(rest[0])
            or re.match(r"^\d+[smh]?$", rest[0])
        ):
            rest = rest[1:]
        yield head
        yield from unwrap(rest)
    else:
        if "-exec" in words and words.index("-exec") + 1 < len(words):
            yield from unwrap(words[words.index("-exec") + 1 :])
        yield executable_key(words)


def tool_scripts(name, args):
    """Yield `(source, script)` for shell in a tool call; `(source, None)` for other code."""
    if name == "bash":
        yield "bash", args.get("command") or ""
    elif name in ("ctx_execute", "ctx_execute_file"):
        language = args.get("language", "?")
        if language in SHELL_LANGUAGES:
            yield name, args.get("code") or ""
        else:
            yield f"{name}: {language}", None
    elif name == "ctx_batch_execute":
        for item in args.get("commands") or []:
            yield name, item.get("command") or "" if isinstance(item, dict) else ""


def main():
    counts, sessions, sources = (collections.Counter() for _ in range(3))
    scripts = unparsed = 0
    files = [f for root in sys.argv[1:] for f in pathlib.Path(root).rglob("*.jsonl")]
    for path in files:
        seen = set()
        for line in path.read_text(errors="replace").splitlines():
            entry = json.loads(line)
            if entry.get("type") != "message" or entry["message"].get("role") != "assistant":
                continue
            for block in entry["message"].get("content") or []:
                if block.get("type") != "toolCall" or not isinstance(block.get("arguments"), dict):
                    continue
                for source, script in tool_scripts(block.get("name"), block["arguments"]):
                    sources[source] += 1
                    if script is None:
                        continue
                    scripts += 1
                    try:
                        keys = list(commands_in(script))
                    except ValueError:
                        unparsed += 1
                        continue
                    # A leading dash is a `find` action left over after `-exec ... \\;`.
                    for key in (key for key in keys if not key.startswith("-")):
                        counts[key] += 1
                        seen.add(key)
        sessions.update(seen)
    print(f"sessions {len(files)}; shell scripts {scripts}; unparsed {unparsed}")
    print("\nSOURCES")
    for source, count in sources.most_common():
        print(f"  {count:6}  {source}")
    print("\nCOMMANDS: uses, sessions, command")
    for key, count in counts.most_common():
        print(f"  {count:6} {sessions[key]:4}  {key}")


main()
