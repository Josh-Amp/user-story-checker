# Changelog

## 0.2.1 (2026-10-21)

- "Start here" guide in the README for people who don't code: add the skill to Claude, or copy and paste the instructions into any AI chat
- `story-readiness.zip`, the skill ready to upload to Claude, with a test that fails if it drifts from `skill/story-readiness/SKILL.md`

## 0.2.0 (2026-10-21)

Stories now get a full review, not just a score.

- Every result has a one-line `verdict`, an INVEST scorecard (`invest`), findings for the role, want, benefit and acceptance criteria (`parts`), and a going-forward checklist (`tips`)
- New findings: generic roles, implementation terms in the want or criteria, a benefit that repeats the want, scope words such as "only", a single happy-path scenario, and too many scenarios
- Vague goal words in the want and criteria: cleaned up, streamlined, improved, better, enhanced, optimized, seamless, modernized
- A story is Ready only if no INVEST check fails, as well as scoring 80+ with Given / When / Then
- "So I can", "so we can", "in order to" and "I need" are accepted in the story format
- `--markdown` on the command line, and a new `review_story` MCP tool, write the review as Markdown
- The `story-readiness` skill writes reviews in the same format, adding a rewrite, notes for the conversation and open questions
- New sample story (STORY-4) and eight new tests

## 0.1.0 (2026-10-14)

First release.

- Story scoring rules: format, Gherkin acceptance criteria, vague wording, size
- Command-line report for a JSON file of stories
- MCP server with `check_story` and `check_backlog` tools
- Claude skill `story-readiness` for backlog grooming reviews
- Five tests and a GitHub Actions workflow that runs them on every push
- Documentation: README, architecture, scoring rules
