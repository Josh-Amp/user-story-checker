---
name: story-readiness
description: Review user stories or a backlog for sprint readiness. Use when someone asks whether stories are ready, wants acceptance criteria reviewed, or pastes backlog items for grooming.
---

# Story readiness review

Use this when reviewing user stories before sprint planning or backlog grooming.

## Steps

1. Collect each story with its ID and acceptance criteria. If acceptance criteria are missing, note it rather than inventing them.
2. If the `story-checker` MCP server is connected, call `check_backlog` with all the stories (or `check_story` for one). Otherwise apply the same four checks by hand:
   - Story uses "As a <role>, I want <goal>, so that <benefit>"
   - Acceptance criteria have Given, When and Then
   - No vague, untestable words (fast, easy, intuitive, etc.)
   - Story is under 60 words; longer ones may need splitting
3. Report back as a short table: ID, score, Ready / Needs work, and the main problem.
4. For each story that needs work, suggest a rewrite. Mark any detail you had to assume (a role, a number, a threshold) as "[confirm with Product Lead]" instead of presenting it as fact.
5. End with open questions to raise with the Product Lead, such as scope, dependencies or missing data. Escalate them; don't resolve them yourself.
