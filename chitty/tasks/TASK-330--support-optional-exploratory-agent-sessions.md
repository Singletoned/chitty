---
title: Support optional exploratory agent sessions
status: planning
priority: medium
created: 2026-11-14
---

## Description

Agents are currently shaped around Chitty ticket work and review flows. Add a PoC/exploratory mode for sessions where an agent may use Chitty when useful, but is not required to claim, update, or complete a ticket. Existing work and review workflows must retain their current requirements.

## Acceptance Criteria

- [ ] A user can start an agent in an explicitly named exploratory or PoC mode without supplying a Chitty ticket ID.
- [ ] The exploratory mode tells the agent that Chitty use is optional and does not require ticket lifecycle changes for the session to succeed.
- [ ] Existing work and review modes continue to require their current ticket and lifecycle behavior.
- [ ] Automated tests cover exploratory-mode invocation and prove that the existing work and review paths are unchanged.

## History

- 2026-11-14T13:39:35Z jolly-umber-badger → planning
