---
title: Stop `chitty check` warning about escaped asterisks and underscores
status: cold-read
created: 2026-11-21
---

## Description

`chitty check` warns about a literal `*` or `_` that formatters may turn into emphasis (`_markdown_warnings` in `src/chitty/check.py`). It also warns about an escaped `\*`, which is already safe: it scans `MARKDOWN.parseInline(text)` text children, and markdown-it's `text_join` rule merges the escape into the surrounding text, so `static/photos/\*.jpg` reads as `static/photos/*.jpg`. Found 2026-11-21 by the cold read of `TASK-529`, which will make Chitty store such asterisks escaped; without this fix every escaped ticket would still warn.

Decision: scan with a second parser, `MarkdownIt("commonmark").disable("text_join")` (a module-level constant next to `MARKDOWN`), for the delimiter loop only. Escapes then stay separate `text_special` tokens, which the loop already skips because it only reads `text` children. Planner probe 2026-11-21: with `text_join` disabled, `a/\*.jpg and b/*.png` parses to `text 'a/'`, `text_special '*'` (markup `\*`), `text '.jpg and b/*.png'`. Leave the indented-paragraph warning and everything else in the function unchanged.

Out of scope: `check` also scans text that is inside indented code blocks, because it uses `parseInline` over block text (a planner fuzz found lone `*` in indented code still warns). That is existing behaviour and stays.

Tests in `tests/test_check.py`, writing ticket files directly as its other Markdown-warning tests do (near line 117): a Description `static/photos/\*.jpg` gives no `literal '*'` warning; `static/photos/\_x\_.jpg` gives no `literal '_'` warning; `static/photos/*.jpg` still gives the `literal '*'` warning; `a\* and files/*.jpg` still gives it (once). All four results were checked by a planner probe on 2026-11-21 with the decided parser. (Two lone asterisks such as `a/*.jpg and c/*.png` pair as emphasis and never warn; do not use them.) No property: a fixed parser setting, with each case listed. The two escaped cases must fail before the change.

## Acceptance Criteria

- [ ] The two escaped examples give no delimiter warning and fail before the change; the two unescaped examples still warn; `make check` passes

## History

- 2026-11-21T23:59:28Z lively-zinc-newt → cold-read
- 2026-11-21T23:59:45Z lively-zinc-newt: changed description
