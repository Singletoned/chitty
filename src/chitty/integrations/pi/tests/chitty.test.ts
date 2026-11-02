import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  chittyPrompt,
  continuationPrompt,
  hasActionableTickets,
  isFailedAssistantResponse,
  isNoMoreWorkResponse,
  parseMode,
  setPiSessionIdentity,
  hasNewAssistantResponse,
} from "../chitty.ts";

const TICKETS = JSON.stringify([
  { id: "TASK-1", status: "todo" },
  { id: "TASK-2", status: "doing" },
  { id: "TASK-3", status: "review" },
  { id: "TASK-4", status: "blocked" },
]);

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

test("selects tickets only from the active mode", () => {
  assert.equal(hasActionableTickets(TICKETS, "work"), true);
  assert.equal(hasActionableTickets(TICKETS, "review"), true);
  assert.equal(
    hasActionableTickets(JSON.stringify([{ status: "review" }]), "work"),
    false,
  );
  assert.equal(
    hasActionableTickets(JSON.stringify([{ status: "todo" }]), "review"),
    false,
  );
});

test("leaves human tickets for people", () => {
  assert.equal(
    hasActionableTickets(
      JSON.stringify([{ status: "todo", context: "human" }]),
      "work",
    ),
    false,
  );
  assert.match(chittyPrompt("work"), /`human` tickets/);
});

test("chooses cheap defaults instead of blocking", () => {
  for (const prompt of [chittyPrompt("work"), continuationPrompt("work")]) {
    assert.match(prompt, /sensible default/);
    assert.match(prompt, /comment the code/);
  }
});

test("rejects invalid Chitty ticket-list output", () => {
  assert.throws(() => hasActionableTickets("not JSON", "work"), /invalid JSON/);
  assert.throws(() => hasActionableTickets("{}", "work"), /ticket list/);
});

test("uses work mode by default and accepts review mode", () => {
  assert.equal(parseMode(""), "work");
  assert.equal(parseMode("work"), "work");
  assert.equal(parseMode("review"), "review");
  assert.throws(() => parseMode("anything"), /Usage/);
});

test("gives work agents only implementation tickets", () => {
  const prompt = chittyPrompt("work");

  assert.match(prompt, /`todo` or `doing`/);
  assert.match(prompt, /do not review tickets/);
  assert.match(prompt, /inspect several upcoming actionable tickets/);
  assert.match(prompt, /highest-priority tickets/);
  assert.match(prompt, /ready for review/);
  assert.match(prompt, /completely different agent/);
  assert.match(prompt, /never a subagent of the implementation agent/);
  assert.match(prompt, /mark the ticket blocked/);
  assert.match(prompt, /NO MORE WORK/);
  assert.doesNotMatch(prompt, /chitty pull/);
});

test("gives review agents only independent review tickets", () => {
  const prompt = chittyPrompt("review");

  assert.match(prompt, /status is `review`/);
  assert.match(prompt, /highest-priority tickets first/);
  assert.match(prompt, /Never review work you have done/);
  assert.match(prompt, /Reviewed: \.\.\./);
  assert.match(prompt, /-s doing/);
  assert.match(prompt, /NO MORE WORK/);
});

test("uses Pi's public session ID API", () => {
  const extension = readFileSync(new URL("../chitty.ts", import.meta.url), "utf8");

  assert.match(extension, /sessionManager\.getSessionId\(\)/);
  assert.doesNotMatch(extension, /sessionManager\.sessionId/);
});

test("stops continuation when a triggered turn produces no assistant response", () => {
  assert.equal(hasNewAssistantResponse(4, 4), false);
  assert.equal(hasNewAssistantResponse(4, 5), true);
});

test("stops continuation after failed assistant turns", () => {
  assert.equal(isFailedAssistantResponse("error"), true);
  assert.equal(isFailedAssistantResponse("aborted"), true);
  assert.equal(isFailedAssistantResponse("end_turn"), false);
  assert.equal(isFailedAssistantResponse(undefined), false);
});

test("stops when the agent says no more work", () => {
  assert.equal(isNoMoreWorkResponse("NO MORE WORK"), true);
  assert.equal(isNoMoreWorkResponse("Completed everything.\nNO MORE WORK"), true);
  assert.equal(isNoMoreWorkResponse("No more work"), false);
});

test("continues each mode with its appropriate workflow", () => {
  assert.match(continuationPrompt("work"), /move that ticket to blocked/);

  const review = continuationPrompt("review");
  assert.match(review, /Never review work you have done/);
  assert.match(review, /move it to doing/);
  assert.match(review, /"NO MORE WORK"/);
});
