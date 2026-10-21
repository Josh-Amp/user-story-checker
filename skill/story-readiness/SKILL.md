---
name: story-readiness
description: Review user stories or a backlog for sprint readiness. Use when someone asks whether stories are ready, wants a story critiqued or acceptance criteria reviewed, or pastes backlog items for grooming.
---

# Story readiness review

Use this when reviewing user stories before sprint planning or backlog grooming, or when someone asks how good a single story is.

## Steps

1. Collect each story with its ID and acceptance criteria. If acceptance criteria are missing, note it rather than inventing them.
2. If the `story-checker` MCP server is connected, call `check_backlog` with all the stories, or `check_story` for one. `review_story` returns the single-story review below as Markdown, ready to build on. If the server isn't connected, apply the same checks by hand:
   - Story uses "As a <role>, I want <goal>, so that <benefit>" ("so I can" is fine too)
   - Acceptance criteria have Given, When and Then
   - No vague, untestable words (fast, easy, intuitive, cleaned up, streamlined, improved, etc.)
   - Story is 60 words or fewer; longer ones may need splitting
   - The INVEST checks and the part by part questions below
3. If the story is about a product you can see (a repo, a site, a document), look at the real thing before judging. Name what the change would actually add or remove, such as "this would delete the goal tracker", rather than reviewing the wording alone.
4. Report in the format below. For a backlog, open with a short table (ID, score, Ready / Needs work, main problem) and write the full format only for the stories that need work.

## Review format

Lead with the answer, then back it up. Keep sentences short and plain.

1. **Verdict.** One or two sentences: ready or not, and the main reasons. Never open with "This review covers…".
2. **The story as submitted.** Quote it with its acceptance criteria.
3. **Scorecard.** A table of the six INVEST checks (Independent, Negotiable, Valuable, Estimable, Small, Testable), each with Pass, Fail, Unclear or Partly and a one-line reason. Say how many it passes. The tool's results are pattern-based: confirm or overrule them with your own judgment, and say why when you overrule one.
4. **Part by part.** A short paragraph each for:
   - **Role.** Is it a real persona with distinct needs, or "a user"? Whose need is it really? "As the site owner" is fine when that's the truth.
   - **Want.** Is it a capability the person gains, or a solution or judgement word ("cleaned up")?
   - **Benefit.** Does "so that" add the outcome or value, or repeat the want?
   - **Acceptance criteria.** Observable results or implementation terms (API, JSON)? Do words like "only" or "all" hide a removal? Is there an unhappy path (failure, empty data, permissions)? Which knock-on changes go unmentioned (navigation, headings, copy, links)? Does each Given set up a state worth testing?
5. **A rewrite.** The story in full ("As a / I want / so that"), then numbered acceptance criteria, each with a short bold name and Given / When / Then. Include at least one unhappy path and any knock-on changes. State the assumption the rewrite rests on, such as the audience or whether something is removed, and mark details you had to guess with "[confirm with Product Lead]".
6. **Notes for the conversation.** Things that aren't criteria but need deciding, such as data freshness or what happens to removed content.
7. **Going forward.** A numbered checklist of the habits this story showed it needs (the tool's `tips`), so the writer improves the next story, not just this one.
8. **Open questions.** Questions for the Product Lead about scope, dependencies or missing data. Escalate them; don't resolve them yourself.

If the review runs longer than a screen, put it in a document and reply with the verdict and a link.
