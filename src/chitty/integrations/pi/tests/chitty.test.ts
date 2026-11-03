import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import chitty, {
  chittyPrompt,
  continuationPrompt,
  isFailedAssistantResponse,
  parseChittyCommand,
  parseChittyFlag,
  setPiSessionIdentity,
  settlementDecision,
} from "../chitty.ts";

test("sets the Pi session identity for child processes", () => {
  const previous = process.env.CHITTY_PI_SESSION_ID;
  try {
    delete process.env.CHITTY_PI_SESSION_ID;
    setPiSessionIdentity("parent-session");
    assert.equal(process.env.CHITTY_PI_SESSION_ID, "parent-session");
    setPiSessionIdentity("child-session");
    assert.equal(process.env.CHITTY_PI_SESSION_ID, "parent-session");
  } finally {
    if (previous === undefined) delete process.env.CHITTY_PI_SESSION_ID;
    else process.env.CHITTY_PI_SESSION_ID = previous;
  }
});

test("parses a mode and ticket ID from /chitty", () => {
  assert.deepEqual(parseChittyCommand("work TASK-12"), {
    mode: "work",
    ticketId: "TASK-12",
  });
  assert.deepEqual(parseChittyCommand(" review 12 "), {
    mode: "review",
    ticketId: "12",
  });
});

test("rejects /chitty without an ID or with an unknown mode", () => {
  assert.throws(() => parseChittyCommand(""), /Usage/);
  assert.throws(() => parseChittyCommand("work"), /Usage/);
  assert.throws(() => parseChittyCommand("unknown TASK-12"), /Usage/);
  assert.throws(() => parseChittyCommand("work TASK-12 extra"), /Usage/);
});

test("parses Chitty ticket flags and rejects missing IDs", () => {
  assert.equal(parseChittyFlag(undefined, "--chitty-work"), undefined);
  assert.equal(parseChittyFlag("TASK-12", "--chitty-work"), "TASK-12");
  assert.throws(() => parseChittyFlag("", "--chitty-work"), /requires a ticket ID/);
  assert.throws(() => parseChittyFlag(true, "--chitty-work"), /requires a ticket ID/);
});

test("rejects an unknown ticket flag before starting an agent turn", async () => {
  for (const flag of ["chitty-work", "chitty-review"]) {
    let sessionStart:
      | ((event: unknown, ctx: unknown) => Promise<void> | void)
      | undefined;
    const sentMessages: string[] = [];
    const pi = {
      appendEntry: () => {},
      exec: async () => ({
        code: 1,
        stdout: "",
        stderr: "ticket not found",
      }),
      getFlag: (name: string) => (name === flag ? "TASK-999" : undefined),
      on: (event: string, handler: (event: unknown, ctx: unknown) => Promise<void> | void) => {
        if (event === "session_start") sessionStart = handler;
        return () => {};
      },
      registerCommand: () => {},
      registerFlag: () => {},
      sendMessage: () => {},
      sendUserMessage: (message: string) => sentMessages.push(message),
    };
    chitty(pi as Parameters<typeof chitty>[0]);

    assert.ok(sessionStart);
    await assert.rejects(
      sessionStart(
        {},
        {
          cwd: process.cwd(),
          sessionManager: {
            getBranch: () => [],
            getSessionId: () => "test-session",
          },
        },
      ),
      /chitty show TASK-999 --json failed/,
    );
    assert.deepEqual(sentMessages, []);
  }
});

test("shuts down without starting when a flagged ticket has left its stage", async () => {
  for (const [flag, status] of [
    ["chitty-work", "review"],
    ["chitty-review", "doing"],
  ]) {
    let sessionStart:
      | ((event: unknown, ctx: unknown) => Promise<void> | void)
      | undefined;
    const sentMessages: string[] = [];
    const notifications: string[] = [];
    let shutdowns = 0;
    const pi = {
      appendEntry: () => {},
      exec: async () => ({
        code: 0,
        stdout: JSON.stringify({ status }),
        stderr: "",
      }),
      getFlag: (name: string) => (name === flag ? "TASK-12" : undefined),
      on: (event: string, handler: (event: unknown, ctx: unknown) => Promise<void> | void) => {
        if (event === "session_start") sessionStart = handler;
        return () => {};
      },
      registerCommand: () => {},
      registerFlag: () => {},
      sendMessage: () => {},
      sendUserMessage: (message: string) => sentMessages.push(message),
    };
    chitty(pi as Parameters<typeof chitty>[0]);

    assert.ok(sessionStart);
    await sessionStart(
      {},
      {
        cwd: process.cwd(),
        sessionManager: {
          getBranch: () => [],
          getSessionId: () => "test-session",
        },
        shutdown: () => shutdowns++,
        ui: { notify: (message: string) => notifications.push(message) },
      },
    );
    assert.deepEqual(sentMessages, []);
    assert.deepEqual(notifications, [
      `Chitty continuation stopped: ticket left ${flag === "chitty-work" ? "work" : "review"} with status ${status}.`,
    ]);
    assert.equal(shutdowns, 1);
  }
});

test("settles work after its ticket leaves todo or doing", () => {
  for (const status of ["review", "blocked", "done"]) {
    assert.deepEqual(settlementDecision("work", status, 0), {
      action: "shutdown",
      reason: `ticket left work with status ${status}`,
    });
  }
  assert.deepEqual(settlementDecision("work", "doing", 0), {
    action: "continue",
  });
});

test("settles review after its ticket leaves review", () => {
  for (const status of ["doing", "blocked", "done"]) {
    assert.deepEqual(settlementDecision("review", status, 0), {
      action: "shutdown",
      reason: `ticket left review with status ${status}`,
    });
  }
  assert.deepEqual(settlementDecision("review", "review", 0), {
    action: "continue",
  });
});

test("does not continue past the cap or an assistant error", () => {
  assert.deepEqual(settlementDecision("work", "doing", 5), {
    action: "shutdown",
    reason: "reached continuation limit",
  });
  assert.deepEqual(settlementDecision("review", "review", 0, "error"), {
    action: "shutdown",
    reason: "agent response ended with error",
  });
});

test("leaves Pi open when a human aborts", () => {
  assert.deepEqual(settlementDecision("work", "doing", 0, undefined, true), {
    action: "stop",
    reason: "human aborted the run",
  });
});

test("recognizes only assistant errors as terminal", () => {
  assert.equal(isFailedAssistantResponse("error"), true);
  assert.equal(isFailedAssistantResponse("aborted"), false);
  assert.equal(isFailedAssistantResponse("end_turn"), false);
  assert.equal(isFailedAssistantResponse(undefined), false);
});

test("work and review prompts name one ticket without choosing another", () => {
  const ticketId = "TASK-12";
  for (const mode of ["work", "review"] as const) {
    for (const prompt of [
      chittyPrompt(mode, ticketId),
      continuationPrompt(mode, ticketId),
    ]) {
      assert.match(prompt, /TASK-12/);
      assert.doesNotMatch(prompt, /another ticket/i);
      assert.doesNotMatch(prompt, /NO MORE WORK/);
    }
  }
});

test("gives work agents the ticket implementation workflow", () => {
  const prompt = chittyPrompt("work", "TASK-12");

  assert.match(prompt, /Create a branch and worktree/);
  assert.match(prompt, /Never implement in the main checkout/);
  assert.match(prompt, /Commit the `doing` claim/);
  assert.match(prompt, /Tick a criterion only after verifying it/);
  assert.match(prompt, /Re-check every criterion before setting `review`/);
  assert.match(prompt, /mark the ticket blocked/);
});

test("gives review agents the ticket review workflow", () => {
  const prompt = chittyPrompt("review", "TASK-12");

  assert.match(prompt, /Never review work you have done/);
  assert.match(prompt, /ticket's branch worktree/);
  assert.match(prompt, /merge its branch into `main`/);
  assert.match(prompt, /Check every criterion/);
  assert.match(prompt, /`--uncheck` each failed criterion/);
});

test("uses Pi's public session ID API", () => {
  const extension = readFileSync(new URL("../chitty.ts", import.meta.url), "utf8");

  assert.match(extension, /sessionManager\.getSessionId\(\)/);
  assert.doesNotMatch(extension, /sessionManager\.sessionId/);
});
