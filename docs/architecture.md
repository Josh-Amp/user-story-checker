# Architecture

Story Checker has three layers. Each one can be used on its own.

## 1. Rules: `story_checker.py`

Plain Python with no third-party dependencies.

- `check_story(story, acceptance_criteria)` runs four checks and returns a dictionary:
  - `score`: 0 to 100
  - `ready`: `True` if the score is 80+ and Given / When / Then are all present
  - `passes`: the checks that passed, in plain English
  - `problems`: the checks that failed, in plain English
- `check_backlog(stories)` runs `check_story` on each item and adds a summary (`total`, `ready`, `average_score`).
- Running the file directly (`python3 story_checker.py file.json`) prints a readable report.

Keeping the rules separate means they can be tested without any AI tooling, and they could later be reused in a script, a web page, or a Jira integration.

## 2. MCP server: `server.py`

[MCP (Model Context Protocol)](https://modelcontextprotocol.io) is an open standard that lets AI applications call external tools. An MCP server describes its tools (name, inputs, description) and the AI app decides when to call them.

`server.py` registers two tools with the `mcp` Python package:

| Tool | Calls |
|---|---|
| `check_story` | `story_checker.check_story` |
| `check_backlog` | `story_checker.check_backlog` |

The server uses the **stdio** transport: the AI app (for example Claude Desktop) starts `server.py` as a background process and exchanges JSON-RPC messages with it over stdin and stdout. Nothing is sent over the network.

The tool descriptions (the docstrings in `server.py`) matter. They're what the AI reads to decide when and how to use each tool.

## 3. Skill: `skill/story-readiness/SKILL.md`

A Claude skill is a folder of instructions that Claude loads when a task matches the skill's `description`. The MCP server supplies *capabilities* (the tools). The skill supplies *process*: how a business analyst would actually run a readiness review.

The skill tells Claude to:

1. Collect the stories and note missing acceptance criteria rather than inventing them
2. Call the MCP tools if connected, or apply the same checks by hand if not
3. Report a short table of ID, score, status and main problem
4. Suggest rewrites, marking assumed details as "[confirm with Product Lead]"
5. List open questions to escalate, rather than resolving them alone

## Request flow

```
User asks Claude to review stories
  → Claude matches the request to the story-readiness skill
  → Skill says: call check_backlog
  → Claude sends a tool call to server.py over MCP
  → server.py calls story_checker.check_backlog
  → Results return to Claude
  → Claude formats the table, rewrites and open questions
```
