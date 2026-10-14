"""
MCP server that exposes the story checker as tools an AI assistant can call.

MCP (Model Context Protocol) is a standard way to give an AI model tools.
This server offers two:
- check_story: score one user story
- check_backlog: score a list of stories and summarise readiness

Run:  python server.py   (it talks to the AI app over stdin/stdout)
"""

from mcp.server.mcpserver import MCPServer  # mcp 2.x (was FastMCP in 1.x)

import story_checker

mcp = MCPServer("story-checker")


@mcp.tool()
def check_story(story: str, acceptance_criteria: str = "") -> dict:
    """Score a user story (0-100) for format, Gherkin acceptance criteria,
    vague wording and size. Returns passes, problems and whether it's ready."""
    return story_checker.check_story(story, acceptance_criteria)


@mcp.tool()
def check_backlog(stories: list[dict]) -> dict:
    """Score a list of stories. Each item: {"id", "story", "acceptance_criteria"}.
    Returns how many are ready and the average score."""
    return story_checker.check_backlog(stories)


if __name__ == "__main__":
    mcp.run()
