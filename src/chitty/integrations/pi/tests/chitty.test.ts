import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import chitty, {
  continuationPrompt,
  isFailedAssistantResponse,
  parseChittyCommand,
  parseChittyFlag,
  requireLinkedWorktree,
  setPiSessionIdentity,
  settlementDecision,
  sumSessionUsage,
} from "../chitty.ts";

function assistantEntry(
  provider: string,
  model: string,
  usage?: { input: number; output: number; cacheRead: number; cacheWrite: number; cost: { total: number } },
) {
  return { type: "message", message: { role: "assistant", provider, model, usage } };
}

const usageEntries = [
  assistantEntry("anthropic", "claude", { input: 2, output: 3, cacheRead: 5, cacheWrite: 7, cost: { total: 0.11 } }),
  assistantEntry("anthropic", "claude", { input: 11, output: 13, cacheRead: 17, cacheWrite: 19, cost: { total: 0.23 } }),
  assistantEntry("openai", "gpt", { input: 23, output: 29, cacheRead: 31, cacheWrite: 37, cost: { total: 0.41 } }),
  assistantEntry("anthropic", "failed"),
];

const expectedUsage = [
  { provider: "anthropic", model: "claude", input: 13, output: 16, cacheRead: 22, cacheWrite: 26, cost: 0.34 },
  { provider: "openai", model: "gpt", input: 23, output: 29, cacheRead: 31, cacheWrite: 37, cost: 0.41 },
  { provider: "anthropic", model: "failed", input: 0, output: 0, cacheRead: 0, cacheWrite: 0, cost: 0 },
];

test("sums assistant usage by provider and model", () => {
  assert.deepEqual(sumSessionUsage([...usageEntries, { type: "message", message: { role: "user" } }]), expectedUsage);
});

test("writes and replaces session usage at shutdown", async () => {
  const directory = mkdtempSync(join(tmpdir(), "chitty-usage-"));
  const usageFile = join(directory, "usage.json");
  const previous = process.env.CHITTY_USAGE_FILE;
  let shutdown: ((event: unknown, ctx: unknown) => Promise<void> | void) | undefined;
  const notifications: string[] = [];
  const pi = {
    appendEntry: () => {}, getFlag: () => undefined,
    on: (event: string, handler: (event: unknown, ctx: unknown) => Promise<void> | void) => {
      if (event === "session_shutdown") shutdown = handler;
      return () => {};
    },
    registerCommand: () => {}, registerFlag: () => {}, sendMessage: () => {}, sendUserMessage: () => {},
  };
  const ctx = {
    sessionManager: { getBranch: () => [], getEntries: () => usageEntries, getSessionId: () => "this-session" },
    ui: { notify: (message: string) => notifications.push(message) },
  };

  try {
    process.env.CHITTY_USAGE_FILE = usageFile;
    writeFileSync(usageFile, JSON.stringify({ sessions: { "other-session": [{ provider: "other", model: "kept", input: 1, output: 2, cacheRead: 3, cacheWrite: 4, cost: 0.5 }] } }));
    chitty(pi as Parameters<typeof chitty>[0]);
    assert.ok(shutdown);
    await shutdown({}, ctx);
    assert.deepEqual(JSON.parse(readFileSync(usageFile, "utf8")), {
      sessions: {
        "other-session": [{ provider: "other", model: "kept", input: 1, output: 2, cacheRead: 3, cacheWrite: 4, cost: 0.5 }],
        "this-session": expectedUsage,
      },
    });
    await shutdown({}, ctx);
    assert.equal(JSON.parse(readFileSync(usageFile, "utf8")).sessions["this-session"].length, expectedUsage.length);
    assert.deepEqual(notifications, []);

    const beforeUnset = readFileSync(usageFile, "utf8");
    delete process.env.CHITTY_USAGE_FILE;
    await shutdown({}, ctx);
    assert.equal(readFileSync(usageFile, "utf8"), beforeUnset);
    assert.equal(existsSync(join(directory, "unset.json")), false);
  } finally {
    if (previous === undefined) delete process.env.CHITTY_USAGE_FILE;
    else process.env.CHITTY_USAGE_FILE = previous;
    rmSync(directory, { recursive: true, force: true });
  }
});

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
    const notifications: string[] = [];
    let shutdowns = 0;
    const pi = {
      appendEntry: () => {},
      exec: async (command: string, args: string[]) => {
        if (command === "git") {
          return { code: 0, stdout: args[1] === "--git-dir" ? ".git/worktrees/t\n" : ".git\n", stderr: "" };
        }
        return { code: 1, stdout: "", stderr: "ticket not found" };
      },
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
    await sessionStart(
      {},
      {
        cwd: process.cwd(),
        hasUI: true,
        mode: "tui",
        sessionManager: {
          getBranch: () => [],
          getSessionId: () => "test-session",
        },
        shutdown: () => shutdowns++,
        ui: { notify: (message: string) => notifications.push(message) },
      },
    );
    assert.deepEqual(sentMessages, []);
    assert.match(notifications[0], /chitty show TASK-999 --json failed/);
    assert.equal(shutdowns, 1);
  }
});

test("starts flagged tickets with a UI in TUI mode", async () => {
  for (const [flag, mode, status] of [
    ["chitty-work", "work", "doing"],
    ["chitty-review", "review", "review"],
  ] as const) {
    for (const hasUI of [true]) {
      let sessionStart:
        | ((event: unknown, ctx: unknown) => Promise<void> | void)
        | undefined;
      const sentMessages: string[] = [];
      const pi = {
        appendEntry: () => {},
        exec: async (command: string, args: string[]) => {
          if (command === "git") {
            return {
              code: 0,
              stdout: args[1] === "--git-dir" ? ".git/worktrees/t\\n" : ".git\\n",
              stderr: "",
            };
          }
          return { code: 0, stdout: args[0] === "guide" ? `guide for ${args[1]}\n` : JSON.stringify({ status }), stderr: "" };
        },
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
          hasUI,
          mode: "tui",
          sessionManager: {
            getBranch: () => [],
            getSessionId: () => "test-session",
          },
          shutdown: () => {},
          ui: { notify: () => {} },
        },
      );
      assert.equal(sentMessages.length, hasUI ? 1 : 0, `${flag} with hasUI=${hasUI}`);
      if (hasUI) {
        assert.equal(sentMessages[0], `guide for ${mode}\n`);
      }
    }
  }
});

test("notifies and shuts down when guide fails or is empty", async () => {
  for (const guideResult of [
    { code: 1, stdout: "", stderr: "guide unavailable" },
    { code: 0, stdout: "   ", stderr: "" },
  ]) {
    let commandHandler:
      | ((args: string, ctx: unknown) => Promise<void> | void)
      | undefined;
    const notifications: string[] = [];
    let shutdowns = 0;
    const pi = {
      appendEntry: () => {},
      exec: async (command: string, args: string[]) => {
        if (command === "git") {
          return { code: 0, stdout: args[1] === "--git-dir" ? ".git/worktrees/t\\n" : ".git\\n", stderr: "" };
        }
        if (args[0] === "show") {
          return { code: 0, stdout: JSON.stringify({ status: "doing" }), stderr: "" };
        }
        return guideResult;
      },
      getFlag: () => undefined,
      on: () => () => {},
      registerCommand: (_name: string, command: { handler: typeof commandHandler }) => {
        commandHandler = command.handler;
      },
      registerFlag: () => {},
      sendMessage: () => {},
      sendUserMessage: () => {},
    };
    chitty(pi as Parameters<typeof chitty>[0]);
    assert.ok(commandHandler);
    await commandHandler("work TASK-12", {
      cwd: process.cwd(),
      sessionManager: { getBranch: () => [], getSessionId: () => "test-session" },
      shutdown: () => shutdowns++,
      ui: { notify: (message: string) => notifications.push(message) },
    });
    assert.equal(shutdowns, 1);
    assert.match(notifications[0], /chitty guide work TASK-12/);
  }
});

test("starts flagged tickets only in TUI mode", async () => {
  const previousSessionId = process.env.CHITTY_PI_SESSION_ID;
  try {
    for (const [flag, ticketMode, status] of [
      ["chitty-work", "work", "doing"],
      ["chitty-review", "review", "review"],
    ] as const) {
      for (const mode of ["rpc", "tui"] as const) {
        delete process.env.CHITTY_PI_SESSION_ID;
        let sessionStart:
          | ((event: unknown, ctx: unknown) => Promise<void> | void)
          | undefined;
        const sentMessages: string[] = [];
        const pi = {
          appendEntry: () => {},
          exec: async (command: string, args: string[]) => {
            if (command === "git") {
              return {
                code: 0,
                stdout: args[1] === "--git-dir" ? ".git/worktrees/t\\n" : ".git\\n",
                stderr: "",
              };
            }
            return { code: 0, stdout: args[0] === "guide" ? `guide for ${args[1]}\n` : JSON.stringify({ status }), stderr: "" };
          },
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
            hasUI: true,
            mode,
            sessionManager: {
              getBranch: () => [],
              getSessionId: () => `${flag}-${mode}`,
            },
            shutdown: () => {},
            ui: { notify: () => {} },
          },
        );
        assert.equal(process.env.CHITTY_PI_SESSION_ID, `${flag}-${mode}`);
        assert.equal(sentMessages.length, mode === "tui" ? 1 : 0, `${flag} in ${mode}`);
        if (mode === "tui") {
          assert.equal(sentMessages[0], `guide for ${ticketMode}\n`);
        }
      }
    }
  } finally {
    if (previousSessionId === undefined) delete process.env.CHITTY_PI_SESSION_ID;
    else process.env.CHITTY_PI_SESSION_ID = previousSessionId;
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
      exec: async (command: string, args: string[]) => {
        if (command === "git") {
          return { code: 0, stdout: args[1] === "--git-dir" ? ".git/worktrees/t\n" : ".git\n", stderr: "" };
        }
        return { code: 0, stdout: args[0] === "guide" ? `guide for ${args[1]}\n` : JSON.stringify({ status }), stderr: "" };
      },
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
        hasUI: true,
        mode: "tui",
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

test("refuses Chitty startup outside a linked worktree", async () => {
  const pi = {
    exec: async () => ({ code: 0, stdout: ".git\n", stderr: "" }),
  };
  await assert.rejects(
    requireLinkedWorktree(pi as never, { cwd: process.cwd() } as never),
    /chitty run/,
  );
});

test("refuses Chitty startup in a main-checkout subdirectory", async () => {
  const directory = mkdtempSync(join(tmpdir(), "chitty-main-"));
  // Git reports physical paths, so use one here to isolate its relative-path behavior.
  const physicalDirectory = realpathSync(directory);
  const subdirectory = join(physicalDirectory, "subdirectory");
  mkdirSync(subdirectory);
  execFileSync("git", ["init", "--quiet"], { cwd: physicalDirectory });
  const pi = {
    exec: async (command: string, args: string[], options: { cwd: string }) => ({
      code: 0,
      stdout: execFileSync(command, args, { cwd: options.cwd, encoding: "utf8" }),
      stderr: "",
    }),
  };

  try {
    await assert.rejects(
      requireLinkedWorktree(pi as never, { cwd: subdirectory } as never),
      /chitty run/,
    );
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});

test("exits cleanly when Chitty starts outside a linked worktree", async () => {
  let sessionStart:
    | ((event: unknown, ctx: unknown) => Promise<void> | void)
    | undefined;
  const notifications: string[] = [];
  let shutdowns = 0;
  const sentMessages: string[] = [];
  const pi = {
    appendEntry: () => {},
    exec: async () => ({ code: 0, stdout: ".git\n", stderr: "" }),
    getFlag: (name: string) => (name === "chitty-work" ? "TASK-12" : undefined),
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
      cwd: `${process.cwd()}/subdirectory`,
      hasUI: true,
      mode: "tui",
      sessionManager: { getBranch: () => [], getSessionId: () => "test-session" },
      shutdown: () => shutdowns++,
      ui: { notify: (message: string) => notifications.push(message) },
    },
  );
  assert.deepEqual(sentMessages, []);
  assert.deepEqual(notifications, [
    "Start Chitty with `chitty run`; it prepares a linked ticket worktree.",
  ]);
  assert.equal(shutdowns, 1);
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
    continuationCount: 1,
  });
});

test("review continuation instructions leave landing to chitty run", () => {
  const prompt = continuationPrompt("review", "TASK-151");
  assert.match(prompt, /Never review work you have done/);
  assert.match(prompt, /Do not merge branches or remove branches or worktrees/);
  assert.match(prompt, /`chitty run` lands a passing review/);
  assert.doesNotMatch(prompt, /merge its branch|remove its branch/i);
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
    continuationCount: 1,
  });
});

test("counts only consecutive continuations without ticket progress", () => {
  assert.deepEqual(settlementDecision("work", "doing", 0, false), {
    action: "continue",
    continuationCount: 1,
  });
  assert.deepEqual(settlementDecision("work", "doing", 4, false), {
    action: "shutdown",
    continuationCount: 5,
    reason: "reached continuation limit after 5 consecutive turns without progress",
  });
  assert.deepEqual(settlementDecision("work", "doing", 4, true), {
    action: "continue",
    continuationCount: 0,
  });

  let continuationCount = 0;
  for (let turn = 0; turn < 20; turn += 1) {
    const decision = settlementDecision("work", "doing", continuationCount, true);
    assert.equal(decision.action, "continue");
    assert.equal(decision.continuationCount, 0);
    continuationCount = decision.continuationCount;
  }
});

test("applies the no-progress cap in review mode too", () => {
  assert.deepEqual(settlementDecision("review", "review", 4, false), {
    action: "shutdown",
    continuationCount: 5,
    reason: "reached continuation limit after 5 consecutive turns without progress",
  });
});

test("does not continue after an assistant error", () => {
  assert.deepEqual(settlementDecision("review", "review", 0, false, "error"), {
    action: "shutdown",
    reason: "agent response ended with error",
  });
});

test("leaves Pi open when a human aborts", () => {
  assert.deepEqual(settlementDecision("work", "doing", 0, false, undefined, true), {
    action: "stop",
    reason: "human aborted the run",
  });
});

test("takes a baseline at start and restores progress state for a resumed session", async () => {
  let command:
    | ((args: string, ctx: unknown) => Promise<void> | void)
    | undefined;
  let settled: ((event: { aborted?: boolean }, ctx: unknown) => Promise<void> | void) | undefined;
  let sessionStart:
    | ((event: unknown, ctx: unknown) => Promise<void> | void)
    | undefined;
  const entries: unknown[] = [];
  const output = JSON.stringify({ status: "doing", history: ["baseline"] });
  const pi = {
    appendEntry: (_type: string, state: unknown) => entries.push(state),
    exec: async (command: string, args: string[]) => {
      if (command === "git") {
        return {
          code: 0,
          stdout: args[1] === "--git-dir" ? ".git/worktrees/task-12\n" : ".git\n",
          stderr: "",
        };
      }
      return { code: 0, stdout: output, stderr: "" };
    },
    getFlag: () => undefined,
    on: (event: string, handler: (event: never, ctx: never) => Promise<void> | void) => {
      if (event === "session_start") sessionStart = handler;
      if (event === "agent_settled") settled = handler;
      return () => {};
    },
    registerCommand: (_name: string, definition: { handler: typeof command }) => {
      command = definition.handler;
    },
    registerFlag: () => {},
    sendMessage: () => {},
    sendUserMessage: () => {},
  };
  chitty(pi as Parameters<typeof chitty>[0]);
  const ctx = {
    cwd: process.cwd(),
    isIdle: () => true,
    sessionManager: { getBranch: () => [], getSessionId: () => "test-session" },
    ui: { notify: () => {} },
  };

  assert.ok(command);
  await command("work TASK-12", ctx);
  assert.deepEqual(entries[0], {
    enabled: true,
    mode: "work",
    ticketId: "TASK-12",
    continuationCount: 0,
    ticketHash: createHash("sha256").update(output).digest("hex"),
  });

  const resumedEntries: unknown[] = [];
  const resumedOutput = JSON.stringify({ status: "review", history: ["unchanged"] });
  const resumedState = {
    enabled: true,
    mode: "review",
    ticketId: "TASK-12",
    continuationCount: 3,
    ticketHash: createHash("sha256").update(resumedOutput).digest("hex"),
  };
  const resumedPi = {
    ...pi,
    appendEntry: (_type: string, state: unknown) => resumedEntries.push(state),
    exec: async (command: string, args: string[]) => {
      if (command === "git") {
        return {
          code: 0,
          stdout: args[1] === "--git-dir" ? ".git/worktrees/task-12\n" : ".git\n",
          stderr: "",
        };
      }
      return { code: 0, stdout: resumedOutput, stderr: "" };
    },
  };
  chitty(resumedPi as Parameters<typeof chitty>[0]);
  const resumedCtx = {
    ...ctx,
    sessionManager: {
      getBranch: () => [{ type: "custom", customType: "chitty-state", data: resumedState }],
      getSessionId: () => "test-session",
    },
  };
  assert.ok(sessionStart);
  await sessionStart({}, resumedCtx);
  assert.ok(settled);
  await settled({}, resumedCtx);
  assert.deepEqual(resumedEntries, [{ ...resumedState, continuationCount: 4 }]);
});

test("notifies and shuts down when reading a settled ticket fails", async () => {
  let settled: ((event: { aborted?: boolean }, ctx: unknown) => Promise<void> | void) | undefined;
  let sessionStart:
    | ((event: unknown, ctx: unknown) => Promise<void> | void)
    | undefined;
  const notifications: string[] = [];
  let shutdowns = 0;
  const pi = {
    appendEntry: () => {},
    exec: async () => ({ code: 1, stdout: "", stderr: "ticket not found" }),
    getFlag: () => undefined,
    on: (event: string, handler: (event: never, ctx: never) => Promise<void> | void) => {
      if (event === "session_start") sessionStart = handler;
      if (event === "agent_settled") settled = handler;
      return () => {};
    },
    registerCommand: () => {},
    registerFlag: () => {},
    sendMessage: () => {},
    sendUserMessage: () => {},
  };
  chitty(pi as Parameters<typeof chitty>[0]);
  const ctx = {
    cwd: process.cwd(),
    isIdle: () => true,
    sessionManager: {
      getBranch: () => [{
        type: "custom",
        customType: "chitty-state",
        data: { enabled: true, mode: "work", ticketId: "TASK-12", continuationCount: 2, ticketHash: "old" },
      }],
      getSessionId: () => "test-session",
    },
    shutdown: () => shutdowns++,
    ui: { notify: (message: string) => notifications.push(message) },
  };
  assert.ok(sessionStart);
  await sessionStart({}, ctx);
  assert.ok(settled);
  await settled({}, ctx);
  assert.equal(shutdowns, 1);
  assert.deepEqual(notifications, [
    "Chitty continuation stopped: chitty show TASK-12 --json failed (exit 1): ticket not found.",
  ]);
});

test("recognizes only assistant errors as terminal", () => {
  assert.equal(isFailedAssistantResponse("error"), true);
  assert.equal(isFailedAssistantResponse("aborted"), false);
  assert.equal(isFailedAssistantResponse("end_turn"), false);
  assert.equal(isFailedAssistantResponse(undefined), false);
});

test("continuation prompts name one ticket", () => {
  for (const mode of ["work", "review"] as const) {
    const prompt = continuationPrompt(mode, "TASK-12");
    assert.match(prompt, /TASK-12/);
    assert.doesNotMatch(prompt, /another ticket|NO MORE WORK/i);
  }
});

test("tells work agents to carry on to the next criterion", () => {
  assert.match(continuationPrompt("work", "TASK-12"), /next criterion without stopping to report/);
});

test("uses Pi's public session ID API", () => {
  const extension = readFileSync(new URL("../chitty.ts", import.meta.url), "utf8");

  assert.match(extension, /sessionManager\.getSessionId\(\)/);
  assert.doesNotMatch(extension, /sessionManager\.sessionId/);
});
