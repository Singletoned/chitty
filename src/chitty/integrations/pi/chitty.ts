import type {
  ExtensionAPI,
  ExtensionContext,
} from "@earendil-works/pi-coding-agent";
import type { AssistantMessage } from "@earendil-works/pi-ai";

const STATE_TYPE = "chitty-state";
const CONTINUATION_TYPE = "chitty-continuation";

type ChittyMode = "work" | "review";

type State = {
  enabled: boolean;
  mode: ChittyMode;
};

export default function chitty(pi: ExtensionAPI) {
  let state: State = { enabled: false, mode: "work" };

  pi.registerCommand("chitty", {
    description: "Work or review Chitty tickets",
    handler: async (args) => {
      const mode = parseMode(args);
      state = { enabled: true, mode };
      persistState(pi, state);
      pi.sendUserMessage(chittyPrompt(mode));
    },
  });

  pi.on("session_start", async (_event, ctx) => {
    state = latestState(ctx) ?? { enabled: false, mode: "work" };
  });

  pi.on("agent_settled", async (_event, ctx) => {
    if (!state.enabled || !ctx.isIdle()) return;

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
  const status = (ticket as { status?: unknown }).status;
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
    "If you need feedback or have questions, add them to the ticket, move that ticket to blocked, and pick up another ticket.",
    'If there is no more work to be done, reply "NO MORE WORK".',
  ].join("\n");
}

export function chittyPrompt(mode: ChittyMode): string {
  const modeInstructions =
    mode === "work"
      ? [
          "Only select tickets whose status is `todo` or `doing`; do not review tickets in this mode.",
          "Use `chitty list` and inspect several upcoming actionable tickets with `chitty show <ID>`; prioritize the highest-priority tickets, while considering dependencies and value.",
          "Follow the repository's Chitty guidance: record a plan, mark the ticket doing, work only that ticket, and verify it. Check satisfied acceptance criteria, then mark it done with a summary or ready for review when the repository workflow requires review. Reviews must be done by a completely different agent, never a subagent of the implementation agent.",
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
