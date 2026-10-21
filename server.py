"""
MCP server that exposes the story checker as tools an AI assistant can call.

MCP (Model Context Protocol) is a standard way to give an AI model tools.
This server offers three:
- check_story: score one user story and review it part by part
- check_backlog: score a list of stories and summarise readiness
- review_story: write a full Markdown review of one story

Run:  python server.py   (it talks to the AI app over stdin/stdout)
"""

from mcp.server.mcpserver import MCPServer  # mcp 2.x (was FastMCP in 1.x)

import story_checker

mcp = MCPServer("story-checker")


@mcp.tool()
def check_story(story: str, acceptance_criteria: str = "") -> dict:
    """Score a user story (0-100) for format, Gherkin acceptance criteria,
    vague wording and size, and review it. Returns score, ready, a one-line
    verdict, passes, problems, an INVEST scorecard, findings for each part
    (role, want, benefit, acceptance_criteria) and tips to work on."""
    return story_checker.check_story(story, acceptance_criteria)


@mcp.tool()
def check_backlog(stories: list[dict]) -> dict:
    """Score a list of stories. Each item: {"id", "story", "acceptance_criteria"}.
    Returns how many are ready and the average score."""
    return story_checker.check_backlog(stories)


@mcp.tool()
def review_story(story: str, acceptance_criteria: str = "", story_id: str = "") -> str:
    """Write a full review of one user story as Markdown: verdict, the story
    as submitted, INVEST scorecard, part by part findings and habits to work
    on. Use it as the starting point for a written review; add a rewrite and
    open questions yourself."""
    return story_checker.review_markdown(story, acceptance_criteria, story_id)


if __name__ == "__main__":
    mcp.run()
