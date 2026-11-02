import type {
  ExtensionAPI,
  ExtensionContext,
} from "@earendil-works/pi-coding-agent";
import type { AssistantMessage } from "@earendil-works/pi-ai";

const STATE_TYPE = "chitty-state";
const CONTINUATION_TYPE = "chitty-continuation";
const PI_SESSION_ID_VARIABLE = "CHITTY_PI_SESSION_ID";

type ChittyMode = "work" | "review";

type State = {
  enabled: boolean;
  mode: ChittyMode;
  continuationAssistantCount?: number;
};

export default function chitty(pi: ExtensionAPI) {
  let state: State = { enabled: false, mode: "work" };

  function start(mode: ChittyMode): void {
    state = { enabled: true, mode };
    persistState(pi, state);
    pi.sendUserMessage(chittyPrompt(mode));
  }

  function stopContinuation(ctx: ExtensionContext, reason: string): void {
    state = { ...state, enabled: false, continuationAssistantCount: undefined };
    persistState(pi, state);
    ctx.ui.notify(`Chitty continuation stopped: ${reason}.`, "info");
  }

  pi.registerFlag("chitty-review", {
    description: "Start directly in Chitty review mode",
    type: "boolean",
    default: false,
  });
  pi.registerFlag("chitty-work", {
    description: "Start directly in Chitty work mode",
    type: "boolean",
    default: false,
  });

  pi.registerCommand("chitty", {
    description: "Work or review Chitty tickets",
    handler: async (args) => {
      start(parseMode(args));
    },
  });

  pi.on("session_start", async (_event, ctx) => {
    setPiSessionIdentity(ctx.sessionManager.getSessionId());
    state = latestState(ctx) ?? { enabled: false, mode: "work" };
    // Review wins if both flags are supplied, avoiding accidental work-mode review.
    if (isChittyReviewFlagEnabled(pi.getFlag("chitty-review"))) {
      start("review");
    } else if (isChittyWorkFlagEnabled(pi.getFlag("chitty-work"))) {
      start("work");
    }
  });

  pi.on("agent_settled", async (_event, ctx) => {
    if (!state.enabled || !ctx.isIdle()) return;

    const assistantCount = assistantMessageCount(ctx);
    if (
      state.continuationAssistantCount !== undefined &&
      !hasNewAssistantResponse(state.continuationAssistantCount, assistantCount)
    ) {
      stopContinuation(ctx, "agent did not produce a response");
      return;
    }

    const assistant = latestAssistantMessage(ctx);
    if (assistant && isFailedAssistantResponse(assistant.stopReason)) {
      stopContinuation(ctx, `agent response ended with ${assistant.stopReason}`);
      return;
    }

    if (isNoMoreWorkResponse(latestAssistantText(ctx))) {
      state = { ...state, enabled: false };
      persistState(pi, state);
      return;
    }

    const workRemains = await hasActionableWork(pi, ctx, state.mode);
    if (!workRemains) {
      state = { ...state, enabled: false };
      persistState(pi, state);
      return;
    }

    state = { ...state, continuationAssistantCount: assistantCount };
    persistState(pi, state);
    pi.sendMessage(
      {
        customType: CONTINUATION_TYPE,
        content: continuationPrompt(state.mode),
        display: true,
      },
      { triggerTurn: true },
    );
  });
}

export function setPiSessionIdentity(sessionId: string): void {
  // A subagent inherits its parent's identity, so it cannot review parent work.
  if (!process.env[PI_SESSION_ID_VARIABLE]) {
    process.env[PI_SESSION_ID_VARIABLE] = sessionId;
  }
}

export function isChittyReviewFlagEnabled(value: unknown): boolean {
  return value === true;
}

export function isChittyWorkFlagEnabled(value: unknown): boolean {
  return value === true;
}

export function parseMode(args: string): ChittyMode {
  const mode = args.trim();
  if (mode === "" || mode === "work") return "work";
  if (mode === "review") return "review";
  throw new Error("Usage: /chitty [work|review]");
}

async function hasActionableWork(
  pi: ExtensionAPI,
  ctx: ExtensionContext,
  mode: ChittyMode,
): Promise<boolean> {
  const result = await pi.exec("chitty", ["list", "--json"], {
    cwd: ctx.cwd,
    signal: ctx.signal,
  });
  if (result.code !== 0) {
    throw new Error(
      `chitty list --json failed (exit ${result.code}): ${result.stderr || result.stdout}`,
    );
  }
  return hasActionableTickets(result.stdout, mode);
}

export function hasActionableTickets(
  stdout: string,
  mode: ChittyMode,
): boolean {
  let tickets: unknown;
  try {
    tickets = JSON.parse(stdout);
  } catch (error) {
    throw new Error(
      `chitty list --json returned invalid JSON: ${error instanceof Error ? error.message : String(error)}`,
    );
  }

  if (!Array.isArray(tickets)) {
    throw new Error("chitty list --json returned a value other than a ticket list.");
  }

  return tickets.some((ticket) => isActionableTicket(ticket, mode));
}

function isActionableTicket(ticket: unknown, mode: ChittyMode): boolean {
  if (typeof ticket !== "object" || ticket === null) return false;
  const { status, context } = ticket as { status?: unknown; context?: unknown };
  if (context === "human") return false;
  return mode === "work"
    ? status === "todo" || status === "doing"
    : status === "review";
}

function persistState(pi: ExtensionAPI, state: State): void {
  pi.appendEntry(STATE_TYPE, state);
}

function latestState(ctx: ExtensionContext): State | undefined {
  const entry = ctx.sessionManager
    .getBranch()
    .filter((item) => item.type === "custom" && item.customType === STATE_TYPE)
    .pop() as { data?: unknown } | undefined;

  if (
    typeof entry?.data !== "object" ||
    entry.data === null ||
    typeof (entry.data as Partial<State>).enabled !== "boolean" ||
    !isMode((entry.data as Partial<State>).mode)
  ) {
    return undefined;
  }
  return entry.data as State;
}

function isMode(value: unknown): value is ChittyMode {
  return value === "work" || value === "review";
}

export function isNoMoreWorkResponse(text: string): boolean {
  return text.includes("NO MORE WORK");
}

export function hasNewAssistantResponse(
  previousAssistantCount: number,
  currentAssistantCount: number,
): boolean {
  return currentAssistantCount > previousAssistantCount;
}

export function isFailedAssistantResponse(
  stopReason: AssistantMessage["stopReason"] | undefined,
): boolean {
  return stopReason === "error" || stopReason === "aborted";
}

function assistantMessageCount(ctx: ExtensionContext): number {
  return ctx.sessionManager
    .getBranch()
    .filter(
      (entry) => entry.type === "message" && entry.message.role === "assistant",
    ).length;
}

function latestAssistantText(ctx: ExtensionContext): string {
  const message = latestAssistantMessage(ctx);
  if (!message) return "";

  return message.content
    .filter((content) => content.type === "text")
    .map((content) => content.text)
    .join("\n");
}

function latestAssistantMessage(
  ctx: ExtensionContext,
): AssistantMessage | undefined {
  const branch = ctx.sessionManager.getBranch();
  for (let index = branch.length - 1; index >= 0; index -= 1) {
    const entry = branch[index];
    if (entry.type === "message" && entry.message.role === "assistant") {
      return entry.message;
    }
  }
  return undefined;
}

const DEFAULT_INSTRUCTION =
  "When a question has a sensible default that is cheap to change later, choose it and carry on instead of blocking: record the choice and why in a Chitty note for the reviewer, and comment the code where the default applies, saying how and why it was chosen. Block only when the choice is costly to reverse or needs a person.";

export function continuationPrompt(mode: ChittyMode): string {
  if (mode === "review") {
    return [
      "There are still tickets awaiting review.",
      "Continue reviewing independent work until the ticket passes or fails.",
      "Never review work you have done. If the work passes, mark it done with a `Reviewed:` note. If it fails, move it to doing with a note explaining what must change, then pick up another review ticket.",
      'If there is no more review work to be done, reply "NO MORE WORK".',
    ].join("\n");
  }

  return [
    "There is still actionable Chitty work.",
    "If you are in the middle of a ticket, carry on with it until it is done.",
    DEFAULT_INSTRUCTION,
    "If you need feedback or have questions, add them to the ticket, move that ticket to blocked, and pick up another ticket.",
    'If there is no more work to be done, reply "NO MORE WORK".',
  ].join("\n");
}

export function chittyPrompt(mode: ChittyMode): string {
  const modeInstructions =
    mode === "work"
      ? [
          "Only select tickets whose status is `todo` or `doing`; do not review tickets in this mode.",
          "Leave `human` tickets for people: never select, block or otherwise change them.",
          "Use `chitty list` and inspect several upcoming actionable tickets with `chitty show <ID>`; prioritize the highest-priority tickets, while considering dependencies and value.",
          "Follow the repository's Chitty guidance: record a plan, mark the ticket doing, work only that ticket, and verify it. Check satisfied acceptance criteria, then mark it done with a summary or ready for review when the repository workflow requires review. Reviews must be done by a completely different agent, never a subagent of the implementation agent.",
          DEFAULT_INSTRUCTION,
          "When blocked by an issue or question, add a clear Chitty note explaining the problem, who can resolve it, and what is needed; then mark the ticket blocked. Create a human ticket and dependency when an external human action is required.",
          "For non-actionable backlog tickets, add a note explaining what is needed and leave them backlog.",
          "Keep working sequentially until no tickets remain that you can act on. Then report completed tickets and waiting tickets, including the reason each is waiting, followed by `NO MORE WORK`.",
        ]
      : [
          "Only select tickets whose status is `review`; do not implement tickets in this mode. Review the highest-priority tickets first.",
          "Never review work you have done. Review only independent work, and skip a ticket when you cannot establish that another agent or person implemented it.",
          "Inspect the ticket, its acceptance criteria, changes, and verification independently. Pass it with `chitty edit <ID> -s done --note \"Reviewed: ...\"`; fail it with `chitty edit <ID> -s doing --note \"...\"` explaining what must change.",
          "Keep reviewing sequentially until no independent review tickets remain. Then report passed, failed, and waiting tickets, followed by `NO MORE WORK`.",
        ];

  return [
    "Work through the Chitty tickets in this repository, one at a time.",
    ...modeInstructions,
    "When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`.",
    "When you notice a concrete improvement in this project or another tool, submit it with `chitty suggest` rather than doing unrelated work.",
  ].join("\n");
}
