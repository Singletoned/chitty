---
title: Stop `chitty check` warning about escaped asterisks and underscores
status: doing
created: 2026-11-21
---

## Description

`chitty check` warns about a literal `*` or `_` that formatters may turn into emphasis (`_markdown_warnings` in `src/chitty/check.py`). It also warns about an escaped `\*`, which is already safe: it scans `MARKDOWN.parseInline(text)` text children, and markdown-it's `text_join` rule merges the escape into the surrounding text, so `static/photos/\*.jpg` reads as `static/photos/*.jpg`. Found 2026-11-21 by the cold read of `TASK-529`, which will make Chitty store such asterisks escaped; without this fix every escaped ticket would still warn.

Decision: scan with a second parser, `MarkdownIt("commonmark").disable("text_join")` (a module-level constant next to `MARKDOWN`), for the delimiter loop only. Escapes then stay separate `text_special` tokens, which the loop already skips because it only reads `text` children. Planner probe 2026-11-21: with `text_join` disabled, `a/\*.jpg and b/*.png` parses to `text 'a/'`, `text_special '*'` (markup `\*`), `text '.jpg and b/*.png'`. Leave the indented-paragraph warning and everything else in the function unchanged.

Out of scope: `check` also scans text that is inside indented code blocks, because it uses `parseInline` over block text (a planner fuzz found lone `*` in indented code still warns). That is existing behaviour and stays.

Tests in `tests/test_check.py`, writing ticket files directly as `test_warns_only_for_literal_delimiters_formatters_escape` (near line 112) does: a Description `static/photos/\*.jpg` gives no `literal '*'` warning; `static/photos/\_x\_.jpg` gives no `literal '_'` warning; `static/photos/*.jpg` still gives the `literal '*'` warning; `a\* and files/*.jpg` still gives it (once). A guard case, `snake_case *a and b_c`, gives no `literal '_'` warning (intraword `_` next to a token split; a cold reader found no change between parsers on 20 such inputs). All results were checked by a planner probe on 2026-11-21 with the decided parser. (Two lone asterisks such as `a/*.jpg and c/*.png` pair as emphasis and never warn; do not use them.) No property: a fixed parser setting, with each case listed. The two escaped cases must fail before the change.

## Acceptance Criteria

- [ ] Each Description example gives the stated warning result under the new scan (the two escaped ones no warning, the two unescaped ones the `*` warning, the guard case no `_` warning); the two escaped examples fail on today's code; `make check` passes

## History

- 2026-11-21T23:59:28Z lively-zinc-newt → cold-read
- 2026-11-21T23:59:45Z lively-zinc-newt: changed description
- 2026-11-22T00:00:35Z lively-zinc-newt: changed description, acceptance criteria
- 2026-11-22T00:00:35Z lively-zinc-newt cold-read → todo
- 2026-11-22T00:51:37Z nimble-bronze-marten todo → doing
