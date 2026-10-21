# Architecture

Story Checker has three layers. Each one can be used on its own.

## 1. Rules: `story_checker.py`

Plain Python with no third-party dependencies.

- `check_story(story, acceptance_criteria)` runs four scored checks, then reviews the story, and returns a dictionary:
  - `score`: 0 to 100
  - `ready`: `True` if the score is 80+, Given / When / Then are all present, and no INVEST check fails
  - `verdict`: one sentence, the answer first
  - `passes`: the scored checks that passed, in plain English
  - `problems`: the scored checks that failed, in plain English
  - `invest`: the six INVEST checks, each `{check, result, why}`
  - `parts`: `role`, `want`, `benefit` and `acceptance_criteria`, each with the `text` found and its `findings`
  - `tips`: the going-forward checklist items this story needs
- `check_backlog(stories)` runs `check_story` on each item and adds a summary (`total`, `ready`, `average_score`).
- `review_markdown(story, acceptance_criteria, story_id)` turns one `check_story` result into a Markdown review: verdict, the story as submitted, scorecard, part by part and going forward.
- Running the file directly (`python3 story_checker.py file.json`) prints a readable report; `--markdown` prints a full review of each story instead.

Keeping the rules separate means they can be tested without any AI tooling, and they could later be reused in a script, a web page, or a Jira integration.

## 2. MCP server: `server.py`

[MCP (Model Context Protocol)](https://modelcontextprotocol.io) is an open standard that lets AI applications call external tools. An MCP server describes its tools (name, inputs, description) and the AI app decides when to call them.

`server.py` registers three tools with the `mcp` Python package:

| Tool | Calls |
|---|---|
| `check_story` | `story_checker.check_story` |
| `check_backlog` | `story_checker.check_backlog` |
| `review_story` | `story_checker.review_markdown` |

The server uses the **stdio** transport: the AI app (for example Claude Desktop) starts `server.py` as a background process and exchanges JSON-RPC messages with it over stdin and stdout. Nothing is sent over the network.

The tool descriptions (the docstrings in `server.py`) matter. They're what the AI reads to decide when and how to use each tool.

## 3. Skill: `skill/story-readiness/SKILL.md`

A Claude skill is a folder of instructions that Claude loads when a task matches the skill's `description`. The MCP server supplies *capabilities* (the tools). The skill supplies *process*: how a business analyst would actually run a readiness review.

The skill tells Claude to:

1. Collect the stories and note missing acceptance criteria rather than inventing them
2. Call the MCP tools if connected, or apply the same checks by hand if not
3. Look at the real product when it can, so findings name what a change would actually add or remove
4. For a backlog, open with a short table of ID, score, status and main problem
5. Write each review in a fixed order: verdict, the story as submitted, INVEST scorecard, part by part, a rewrite with full acceptance criteria, notes for the conversation, going forward, and open questions

The tool produces the first four sections and the going-forward list. The skill adds the rest, and confirms or overrules the tool's INVEST results, because a rewrite and open questions need judgment a pattern check doesn't have.

## Request flow

```
User asks Claude to review stories
  → Claude matches the request to the story-readiness skill
  → Skill says: call check_backlog
  → Claude sends a tool call to server.py over MCP
  → server.py calls story_checker.check_backlog
  → Results return to Claude
  → Claude writes the review: verdict, scorecard, part by part,
    rewrite, notes, going forward and open questions
```
