---
title: "Baseline: classify every past review failure by cause"
status: done
priority: high
owner: human
parent: TASK-106
created: 2026-11-03
---

## Description

Hand-run the first retro, so the spec-first pilot has something to be compared with. History shows 23 failed reviews across 14 of 50 reviewed tickets; a quick first pass over the 22 notes it could find gave 14 missed cases, 5 weak tests, 2 branch or merge problems and 1 unmet docs criterion. That pass was rough and read truncated notes, and it did not separate cases the ticket stated from cases it left out, which is the distinction that matters.

Read-only over tickets and Git, apart from this ticket and any tickets it proposes. Do not change rules or prompts here: proposals go to the human.

This is for the planning session, not a worker: it needs judgement about why reviews failed, and it proposes rules for the human. Owner `human` is how `chitty next` and `chitty run` skip it.

Recount rather than trusting the figures above, which were rough and are now out of date: a raw count on 2026-11-04 found `review → doing` 36 times across 21 task files. Count failures from each task's `## History`, including archived tickets, and use notes for the reason. Several failure notes do not say `Review failed`. Include failures up to the day this runs, and say the date. Map the first pass's categories to `PLAN.md`'s causes: criterion 2 is what splits a missed case between `design` and `work`. First-pass yield is reviewed tickets that passed their first review, divided by all reviewed tickets. The report goes in this ticket's notes, and the two candidate proposals below count towards the three.

## Acceptance Criteria

- [x] Every failed review in History is listed with its ticket and one cause from `PLAN.md`, or `unknown` with the reason; the count reconciles with History
- [x] Each failure records whether it cited a stated criterion or a case the ticket left out
- [x] Reports first-pass yield, retries per ticket and failures by cause, and states what it could not measure, including post-`done` escapes
- [x] Proposes at most three changes to standing rules, each naming the failure class it should reduce, for the human to accept or reject

## Plan

Extract every transition and note from `## History` and Git, classify each failure against `PLAN.md`, compute yield, size correlation and Pi cost per phase, then write the report and proposals to the notes. Scripts stay in the session scratchpad.

## Notes

Candidate proposal for the retro: a scripted check that fails when `src/chitty/guide.md` changes without a `__version__` bump. `TASK-104` lost its bump in a rebase with its criterion still ticked, and a reviewer had to spot it.

Second candidate for the retro: a scripted check that `__version__` is above `main`'s when the guide or extension changes. Two tickets bumping to the same version merge silently, and repositories then never learn about the later change.

Cold read by a fresh Sonnet subagent, 2026-11-04. Fixed: which history to count, stale figures, the mapping to causes, a formula for yield, and where the report goes.

Report, data to 2026-11-04 (last commit `92db83f`). Results: 35 failures on 19 of 70 reviewed tickets. First-pass yield is 51 of 70, or 72.9%. Retries are 0.50 per reviewed ticket and 1.84 per failed ticket; the spread is 51 tickets with none, 10 with one, 5 with two, 3 with three and 1 with six. Failures by cause: `work` 16, `design` 9, `tests` 7, `integration` 3, `review` 0, `unknown` 0.

Reconciliation: History has 31 `review → doing` and 3 `review → blocked`, which is 34 on 18 tickets, plus `TASK-79`'s `done → doing`, which its note records as a failed review, making 35 on 19. `TASK-79` had first passed on a self-check. The raw count of 36, now 37, in 22 files also matches prose in `TASK-30`, `TASK-31`, `TASK-64`, `TASK-65` and this ticket: 6 lines, and 4 of the files have no real transition. A second pass over every commit on every branch found no failure transition lost to a rebase or reset. `TASK-80` is in `review` on its branch with no verdict, so it is excluded. So are the 35 `done` tickets with no review verdict, mostly from before `review` existed. All 4 archived tickets were read.

Method: S means a plain reading of the ticket's words already makes the behaviour wrong, including its description; L means it takes something the ticket does not say. S gives `work` or `tests`, and L gives `design`, as criterion 2 requires. First-pass categories map as: missed case to `work` or `design` by that split, weak test to `tests`, branch or merge to `integration`, unmet docs to `work`. Mixed notes take the majority of their findings. Exceptions: `TASK-79` is `work` because a regression needs no statement; `TASK-93` #1 is `work` because it broke a repository rule; `TASK-118` and `TASK-126` #3 are `design` because the criterion itself was at fault; `TASK-49` is `design` because the ticket contradicted itself. I differ from two recorded labels: `TASK-123` #1, whose author's retro says `design`, and `TASK-104` #2, whose note says `work`. Using those labels moves one failure in each case. These classifications are my judgement, from the notes rather than from re-running the code.

Every failure. Cited: S stated, L left out. Kind: defect means behaviour was wrong; deliverable means a stated test, doc or version bump was missing or weak while behaviour was right; stricter means behaviour was right and the reviewer read the criterion more tightly; process means branch, merge or a self-return. Reviewer is the Pi session that failed it: other, same as the worker's, or none found.

| Failure | Cause | Cited | Kind | Reviewer | Finding |
| --- | --- | --- | --- | --- | --- |
| `TASK-31` #1 | work | S | defect | same | upgrade skips `review` on a substring match (crit 2) |
| `TASK-31` #2 | work | S | defect | same | `add` accepts an initial `done` under enforcement (crit 3) |
| `TASK-31` #3 | work | S | defect | same | `pyproject` upgrade mistakes another table's `review` key (crit 2) |
| `TASK-34` #1 | work | S | defect | same | partial deletion loses a claimed suggestion (crit 1) |
| `TASK-34` #2 | work | S | defect | same | `KeyboardInterrupt` bypasses claim recovery (crit 1, description) |
| `TASK-35` #1 | work | S+L | defect | same | `AGENTS.md` bypasses autocommit (crit 3); partial imports and archive history not stated |
| `TASK-35` #2 | design | L | defect | same | writes before the `try` are not rolled back; the ticket never asks for rollback |
| `TASK-43` #1 | design | L | defect | other | only `init` renders the prefix; the ticket named only the managed block; human redesigned |
| `TASK-46` #1 | tests | S | deliverable | other | regression test passes without the fix (crit 4); fix itself correct |
| `TASK-46` #2 | tests | S | deliverable | none | same test still passes without the fix (crit 4) |
| `TASK-46` #3 | tests | S | deliverable | none | same finding again; worker re-verified without changing it |
| `TASK-49` #1 | design | S+L | defect | none | description and crit 4 conflict on `snake_case`, 96 false warnings; MCP drops `severity`, exact pin not stated |
| `TASK-51` #1 | design | L | defect | none | no `project` name gives a bare `AssertionError`; not in the ticket |
| `TASK-77` #1 | work | S | defect | same | failed commit leaves files (description); commented `autocommit = false` not enabled (crit 1) |
| `TASK-79` #1 | work | L | defect | other | string sort scrambles ties; a regression, so `work` though unstated. History shows `done → doing` |
| `TASK-82` #1 | work | S | defect | other | `fix` still writes in a stale repository (crit 3) |
| `TASK-87` #1 | design | L | defect | other | `PI_CODING_AGENT_DIR` ignored; never mentioned in the ticket |
| `TASK-93` #1 | work | L | process | same | worker returned its own ticket 23 seconds later for a missing bump; repository rule, not the ticket. No reviewer |
| `TASK-93` #2 | tests | S | deliverable | other | tests omit `error` and `aborted` turns (crit 1) |
| `TASK-98` #1 | integration | S | process | none | implementation from `67eb452` missing from the tree |
| `TASK-99` #1 | tests | S | deliverable | other | no History assertions for the three paths (crit 2) |
| `TASK-99` #2 | work | S | deliverable | other | `PLAN.md` not updated (crit 3) |
| `TASK-99` #3 | work | S | stricter | other | deleted file's History append, invisible once removed (crit 2) |
| `TASK-104` #1 | integration | L | process | other | conflicts with `TASK-102` after it merged; no criterion involved |
| `TASK-104` #2 | integration | S | deliverable | none | bump dropped by a rebase (crit 4); note says `work`, but the rebase is the earliest stage |
| `TASK-118` #1 | design | S | deliverable | other | criteria describe the local machine, so a branch cannot show them; human forced the pass |
| `TASK-123` #1 | work | S | defect | other | unknown ID starts a turn; in Decisions, no criterion. The author's retro says `design` |
| `TASK-123` #2 | design | L | defect | other | ticket already out of stage still starts a turn; never mentioned |
| `TASK-124` #1 | work | S | defect | other | archived dependency unmet; two tests weaker than their criteria |
| `TASK-126` #1 | tests | S | deliverable | other | tests missing (crit 1, 8), hand run unrecorded (crit 11), `README.md` (crit 13) |
| `TASK-126` #2 | work | S | defect | other | `npm test` fails (crit 5); worktree check wrong in a subdirectory (crit 15) |
| `TASK-126` #3 | design | S | defect | other | actors collide 1 in 289: literal criterion, older fault; human narrowed the criterion |
| `TASK-126` #4 | tests | S | stricter | other | tests exist; reviewer wants claim-branch and ordering assertions (crit 1, 7) |
| `TASK-126` #5 | work | S | deliverable | other | `__version__` not bumped though the unblock note said to (crit 5) |
| `TASK-126` #6 | design | L | defect | other | relative `PATH` entry; human closed it as narrow and moved it to `TASK-136` |

Real defect or stricter reading? 20 of 35 found a real defect in behaviour: 11 on stated behaviour, 7 on cases the ticket left out, 2 on both. Another 10 found a stated deliverable missing or weak while the behaviour was right. Only 2 were a stricter reading in the narrow sense (`TASK-99` #3, `TASK-126` #4), and 3 were process. If the 9 defects touching left-out cases also count as wider than the ticket, the upper figure for "stricter" is 11. No failure was shown to be reviewer error, so `review` is 0, but the human overrode two outcomes: `TASK-118` was forced through and `TASK-126` #6 was closed as narrow. In 11 of the 16 later-round failures, by my reading, the finding already existed at the previous review, including all 6 since `TASK-104` told reviewers to report everything (`TASK-123` #2, `TASK-126` #2 to #6). So reviewers finding more on each pass drives repeat failures more than a stricter reading does.

Do failures rise with criteria or diff size? Yes, moderately, for both. Spearman with failures: 0.30 for criteria at first review, 0.27 for diff size at first review, and 0.26 and 0.23 without `TASK-126`. Total diff size gives 0.42, but rework inflates that. Failed-ticket share by criteria: 0 to 2, 1 of 16 (6%); 3, 4 of 18 (22%); 4, 8 of 20 (40%); 5, 2 of 9 (22%); 6 or more, 4 of 7 (57%). Together, 1 to 3 criteria (0 included) is 5 of 34 (15%) and 4 or more is 14 of 36 (39%). By lines at first review: up to 100, 9 of 44 (20%); 101 to 250, 5 of 17 (29%); 251 to 500, 3 of 6 (50%); over 500, 1 of 1, `TASK-126`. This supports `PLAN.md`'s size limits, though small tickets still fail: lines are added plus removed from `Task:` commits, excluding `chitty/` and `uv.lock`, for 68 of 70 tickets (`TASK-31` and `HUMAN-6` have no such commits). `TASK-98` measures 0 at first review because its code was lost.

What did failed reviews cost? At least $12.35 in main Pi sessions: $3.48 on failing reviews and $8.87 on rework, an average of $0.35 a failure. That is 17% of the $71.58 main-session spend on this repository and 42% of the $29.69 spent on failed tickets. `TASK-126` alone is $4.41, or 36%. Failed tickets cost $1.56 on average against $0.55 for clean ones, but they were already larger: first-pass work averaged $0.81 against $0.44. Clean tickets' passing reviews averaged $0.08 each.

What the cost could not match: 6 failures have no Pi session and were presumably reviewed in Claude Code, which records no cost (`TASK-46` #2 and #3, `TASK-49`, `TASK-51`, `TASK-98`, `TASK-104` #2). Rework after the date-only ones sits in the first-pass figure, so $12.35 is a lower bound. 9 failures happened in the worker's own session, so their review cost is inside rework. Subagents cost another $11.08, $7.07 of it on failed tickets, and are not split by phase. 3 of the 51 clean tickets have no Pi cost. $0.32 matched no ticket, and one scratch-repository session was excluded. Attribution within a session follows the most recent `chitty edit` or `chitty show`, so it is approximate, and planning in the same session counts as first-pass work. Figures are `usage.cost.total` as Pi recorded it for provider `openai-codex`, which may not be the amount billed. Human time and waiting time are not included.

What else could not be measured: post-`done` escapes. There is one reopen (`TASK-79`) and one `escape` label (`TASK-128`), and no audits have run, so nothing shows how many reviewed tickets shipped bugs. `PLAN.md` says to read yield only alongside escapes, so 72.9% cannot yet show whether reviews are too soft or too strict. Yield by first-verdict day shows no trend: 10-27 5 of 8, 10-28 10 of 12, 10-29 2 of 4, 10-31 1 of 1, 11-01 13 of 18, 11-02 7 of 9, 11-03 5 of 9, 11-04 8 of 9. 9 failures came from non-independent reviews, so early passes may also be weak. `TASK-31`, `TASK-34`, `TASK-35` and `TASK-93` were committed in bulk, so the order of their failures is taken from note order.

Proposals for the human to accept or reject; none are applied, and no tickets are opened until then.

1. Fail `make check` when `src/chitty/guide.md`, the Pi extension or the `chitty.toml` template changes unless `__version__` is above `main`'s. This merges the two candidates above, since the second implies the first. Failure class: missed or lost version bump (`TASK-93` #1, `TASK-104` #2, `TASK-126` #5). Two tickets taking the same version would also fail once the second is behind `main`. Scripted, so it adds no prompt rule.

2. Make a review verdict a template: one line per criterion giving pass or fail and the command or test that shows it, which `chitty edit` refuses without on a review verdict. A test criterion passes only with evidence that the test fails without the change. Failure classes: later-round findings that were already visible (11 of 16, unchanged by the prompt rule from `TASK-104`) and `tests` (7, where `TASK-46` failed three times on one test). It overlaps the spec-first pilot in `TASK-109`, so the test-evidence half could be dropped if the pilot is adopted. It replaces a prompt rule rather than adding one.

3. Fail a review only on a stated criterion, a stated part of the description, or a regression. A case the ticket left out becomes a new ticket, as `TASK-126` #6 did by hand. Failure class: left-out cases, `design` (`TASK-35` #2, `TASK-43`, `TASK-51`, `TASK-87`, `TASK-123` #2, `TASK-126` #6). The cost is real: all 6 were real defects, and they would ship and be fixed later rather than before merge. Yield would rise for that reason alone, so judge this one on escapes, and only with the `TASK-111` report in place. This is the proposal I am least sure of.

Reviewed: independently recounted 34 `review → doing` or `review → blocked` History lines on 18 tickets, matching the report, with `TASK-79`'s `done → doing` making 35 on 19. Re-added causes, kinds, cited types, the same-session count and the per-ticket spread from the table, and all match, as do yield and retries. Spot-checked `TASK-46`, `TASK-87` and `TASK-118` against their own notes, and they match. Classifications are judgement and were sampled, not all re-derived. The correlations and costs were not recomputed. One correction: the `TASK-126` #3 row repeats 1 in 289, a figure copied from that ticket; there were 256 names at the time. Proposal 3 needs comparing with the human's later instruction that a reviewer may fail for a demonstrated defect.

Human's decision, 2026-11-04: proposals 1 and 2 accepted, each with its own ticket. Proposal 3 rejected for now, because all 6 failures it would change were real defects, and there is no escape data to judge shipping them. The human added that their remarks are suggestions unless they say otherwise, so my review note's reference to an "instruction" overstates it.

## Summary

Baseline: 35 failed reviews on 19 of 70 reviewed tickets, 72.9% first-pass yield. 30 of 35 found a real defect or a missing stated deliverable, and 2 were a stricter reading. Three proposals await the human; none are applied. Post-`done` escapes could not be measured.

## History

- 2026-11-03T10:27:46Z lively-panda → backlog
- 2026-11-03T10:28:25Z lively-panda: changed acceptance criteria
- 2026-11-03T10:41:02Z lively-panda: changed notes
- 2026-11-03T20:44:58Z lively-panda: changed notes
- 2026-11-04T19:32:41Z mellow-newt: changed owner, description
- 2026-11-04T19:36:35Z mellow-newt: changed description, notes
- 2026-11-04T19:36:36Z mellow-newt backlog → todo
- 2026-11-04T20:10:26Z quick-toad: wrote the plan
- 2026-11-04T20:10:26Z quick-toad todo → doing
- 2026-11-04T20:10:39Z quick-toad: changed notes; ticked acceptance criteria
- 2026-11-04T20:10:39Z quick-toad doing → review
- 2026-11-04T20:33:44Z mellow-newt: changed notes, summary
- 2026-11-04T20:33:44Z mellow-newt review → done
- 2026-11-04T20:45:27Z mellow-newt: changed notes
