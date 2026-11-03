import type {
  ExtensionAPI,
  ExtensionContext,
} from "@earendil-works/pi-coding-agent";
import type { AssistantMessage } from "@earendil-works/pi-ai";

const STATE_TYPE = "chitty-state";
const CONTINUATION_TYPE = "chitty-continuation";
const PI_SESSION_ID_VARIABLE = "CHITTY_PI_SESSION_ID";
export const MAX_CONTINUATIONS = 5;

type ChittyMode = "work" | "review";

type State = {
  enabled: boolean;
  mode: ChittyMode;
  ticketId?: string;
  continuationCount?: number;
};

type ChittyCommand = {
  mode: ChittyMode;
  ticketId: string;
};

type SettlementDecision =
  | { action: "continue" }
  | { action: "shutdown"; reason: string }
  | { action: "stop"; reason: string };

export default function chitty(pi: ExtensionAPI) {
  let state: State = { enabled: false, mode: "work" };

  async function start(
    mode: ChittyMode,
    ticketId: string,
    ctx: ExtensionContext,
  ): Promise<void> {
    await ticketStatus(pi, ctx, ticketId);
    state = { enabled: true, mode, ticketId, continuationCount: 0 };
    persistState(pi, state);
    pi.sendUserMessage(chittyPrompt(mode, ticketId));
  }

  function stopContinuation(
    ctx: ExtensionContext,
    reason: string,
    shutdown: boolean,
  ): void {
    state = { ...state, enabled: false, continuationCount: undefined };
    persistState(pi, state);
    ctx.ui.notify(`Chitty continuation stopped: ${reason}.`, "info");
    if (shutdown) ctx.shutdown();
  }

  pi.registerFlag("chitty-review", {
    description: "Review one Chitty ticket until it leaves review",
    type: "string",
  });
  pi.registerFlag("chitty-work", {
    description: "Work one Chitty ticket until it leaves work",
    type: "string",
  });

  pi.registerCommand("chitty", {
    description: "Work or review one Chitty ticket",
    handler: async (args, ctx) => {
      const { mode, ticketId } = parseChittyCommand(args);
      await start(mode, ticketId, ctx);
    },
  });

  pi.on("session_start", async (_event, ctx) => {
    setPiSessionIdentity(ctx.sessionManager.getSessionId());
    state = latestState(ctx) ?? { enabled: false, mode: "work" };

    const reviewTicket = parseChittyFlag(
      pi.getFlag("chitty-review"),
      "--chitty-review",
    );
    const workTicket = parseChittyFlag(pi.getFlag("chitty-work"), "--chitty-work");
    if (reviewTicket !== undefined && workTicket !== undefined) {
      throw new Error("Use only one of --chitty-work and --chitty-review.");
    }
    if (reviewTicket !== undefined) await start("review", reviewTicket, ctx);
    if (workTicket !== undefined) await start("work", workTicket, ctx);
  });

  pi.on("agent_settled", async (event, ctx) => {
    if (!state.enabled || !ctx.isIdle() || state.ticketId === undefined) return;

    if (event.aborted) {
      stopContinuation(ctx, "human aborted the run", false);
      return;
    }

    const status = await ticketStatus(pi, ctx, state.ticketId);
    const decision = settlementDecision(
      state.mode,
      status,
      state.continuationCount ?? 0,
      latestAssistantMessage(ctx)?.stopReason,
    );
    if (decision.action !== "continue") {
      stopContinuation(
        ctx,
        decision.reason,
        decision.action === "shutdown",
      );
      return;
    }

    state = {
      ...state,
      continuationCount: (state.continuationCount ?? 0) + 1,
    };
    persistState(pi, state);
    pi.sendMessage(
      {
        customType: CONTINUATION_TYPE,
        content: continuationPrompt(state.mode, state.ticketId),
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

export function parseChittyCommand(args: string): ChittyCommand {
  const parts = args.trim().split(/\s+/);
  if (parts.length !== 2 || !isMode(parts[0])) {
    throw new Error("Usage: /chitty work|review ID");
  }
  return { mode: parts[0], ticketId: parts[1] };
}

export function parseChittyFlag(
  value: unknown,
  flag: string,
): string | undefined {
  if (value === undefined) return undefined;
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${flag} requires a ticket ID.`);
  }
  return value.trim();
}

export function settlementDecision(
  mode: ChittyMode,
  status: string,
  continuationCount: number,
  stopReason?: AssistantMessage["stopReason"],
  aborted = false,
): SettlementDecision {
  if (aborted) return { action: "stop", reason: "human aborted the run" };
  if (isFailedAssistantResponse(stopReason)) {
    return { action: "shutdown", reason: `agent response ended with ${stopReason}` };
  }
  if (!isActiveStatus(mode, status)) {
    return {
      action: "shutdown",
      reason: `ticket left ${mode} with status ${status}`,
    };
  }
  if (continuationCount >= MAX_CONTINUATIONS) {
    return { action: "shutdown", reason: "reached continuation limit" };
  }
  return { action: "continue" };
}

export function isFailedAssistantResponse(
  stopReason: AssistantMessage["stopReason"] | undefined,
): boolean {
  return stopReason === "error";
}

async function ticketStatus(
  pi: ExtensionAPI,
  ctx: ExtensionContext,
  ticketId: string,
): Promise<string> {
  const result = await pi.exec("chitty", ["show", ticketId, "--json"], {
    cwd: ctx.cwd,
    signal: ctx.signal,
  });
  if (result.code !== 0) {
    throw new Error(
      `chitty show ${ticketId} --json failed (exit ${result.code}): ${result.stderr || result.stdout}`,
    );
  }

  let ticket: unknown;
  try {
    ticket = JSON.parse(result.stdout);
  } catch (error) {
    throw new Error(
      `chitty show ${ticketId} --json returned invalid JSON: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  if (
    typeof ticket !== "object" ||
    ticket === null ||
    typeof (ticket as { status?: unknown }).status !== "string"
  ) {
    throw new Error(`chitty show ${ticketId} --json returned a ticket without a status.`);
  }
  return (ticket as { status: string }).status;
}

function isActiveStatus(mode: ChittyMode, status: string): boolean {
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
    !isMode((entry.data as Partial<State>).mode) ||
    (entry.data as Partial<State>).ticketId !== undefined &&
      typeof (entry.data as Partial<State>).ticketId !== "string"
  ) {
    return undefined;
  }
  return entry.data as State;
}

function isMode(value: unknown): value is ChittyMode {
  return value === "work" || value === "review";
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

export function continuationPrompt(mode: ChittyMode, ticketId: string): string {
  return [
    `Continue working only on Chitty ticket ${ticketId}.`,
    mode === "work"
      ? "Tick a criterion only after verifying it. Re-check every criterion before setting `review`."
      : "Never review work you have done. Check every criterion, list every failure in one note, and `--uncheck` each failed criterion.",
    "If you need a person to answer a question, record it in a Chitty note and set the ticket to `blocked`; do not end the turn.",
  ].join("\n");
}

export function chittyPrompt(mode: ChittyMode, ticketId: string): string {
  const modeInstructions =
    mode === "work"
      ? [
          "Create a branch and worktree under `.worktrees/` from `main`. Never implement in the main checkout. Commit the `doing` claim on its branch before implementation starts.",
          "Follow the repository's Chitty guidance: record a plan, mark the ticket doing, and verify it. Tick a criterion only after verifying it. Re-check every criterion before setting `review`. Reviews must be done by a completely different agent, never a subagent of the implementation agent.",
          DEFAULT_INSTRUCTION,
          "When blocked by an issue or question, add a clear Chitty note explaining the problem, who can resolve it, and what is needed; then mark the ticket blocked.",
        ]
      : [
          "Never review work you have done. Review in the ticket's branch worktree. Inspect the ticket, its acceptance criteria, changes, and verification independently.",
          "Check every criterion, list every failure in one note, and `--uncheck` each failed criterion. On a pass, merge its branch into `main`, then remove its branch and worktree. Pass it with `chitty edit <ID> -s done --note \"Reviewed: ...\"`; fail it with `chitty edit <ID> -s doing --note \"...\"` explaining what must change.",
        ];

  return [
    `Work only on Chitty ticket ${ticketId}.`,
    ...modeInstructions,
    "When you write a literal single `*` in Markdown, escape it or enclose the pattern in backticks, for example `files/*.jpg`.",
    "When you notice a concrete improvement in this project or another tool, submit it with `chitty suggest` rather than doing unrelated work.",
  ].join("\n");
}
