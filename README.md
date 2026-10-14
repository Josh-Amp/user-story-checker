# User Story Checker

**A user story quality checker for Agile teams, available to AI assistants through an MCP server and a Claude skill.**

[![tests](https://github.com/Josh-Amp/user-story-checker/actions/workflows/tests.yml/badge.svg)](https://github.com/Josh-Amp/user-story-checker/actions/workflows/tests.yml)

Story Checker scores user stories for sprint readiness. It checks whether each story uses the standard format, has testable Gherkin acceptance criteria, avoids vague wording, and is small enough for one sprint. You can run it as a plain Python script, or connect it to an AI assistant such as Claude Desktop so the assistant can check a whole backlog during grooming.

## Why I built it

As a business analyst I have written 150+ Jira tickets, including user stories with Gherkin acceptance criteria. Most rework I saw came from stories that weren't ready: missing "so that" benefits, acceptance criteria with no Given / When / Then, and words like "fast" or "easy" that nobody can test. This project turns those review standards into code. It's also a hands-on way to learn how AI tools are built, through MCP (Model Context Protocol) and Claude skills.

## What it checks

| Check | Points | Why it matters |
|---|---|---|
| "As a &lt;role&gt;, I want &lt;goal&gt;, so that &lt;benefit&gt;" format | 40 | Makes the user and the value explicit |
| Gherkin acceptance criteria (Given / When / Then) | 30 | Gives developers and testers a clear pass/fail test |
| No vague, untestable words (fast, easy, intuitive, etc.) | 20 | Vague words can't be verified in QA |
| Story is 60 words or fewer | 10 | Long stories usually hide more than one story |

A story is **Ready** when it scores 80 or more **and** its acceptance criteria include all of Given, When and Then. See [docs/scoring.md](docs/scoring.md) for the full rules.

## How it fits together

```
 You (in Claude Desktop)
        │  "Are these stories ready for sprint planning?"
        ▼
 Claude  ── follows ──▶  skill/story-readiness/SKILL.md   (the review procedure)
        │
        │  calls tools over MCP (stdin/stdout)
        ▼
 server.py  (MCP server: check_story, check_backlog)
        │
        ▼
 story_checker.py  (the scoring rules, plain Python)
```

- **`story_checker.py`** holds the rules. It has no dependencies and runs on its own.
- **`server.py`** wraps those rules as two MCP tools so any MCP-compatible AI app can call them.
- **`SKILL.md`** tells Claude *how* to run a readiness review: collect stories, call the tools, report a table, suggest rewrites, and list open questions for the Product Lead.

More detail is in [docs/architecture.md](docs/architecture.md).

## Quick start

Requires Python 3.10 or newer.

```bash
git clone https://github.com/Josh-Amp/user-story-checker.git
cd user-story-checker

# 1. Check the sample stories (no install needed)
python3 story_checker.py sample_stories.json

# 2. Run the tests
python3 test_story_checker.py
```

Example output:

```
1 of 3 stories ready | average score 70.0

[STORY-1] score 100 READY
[STORY-2] score 50 NEEDS WORK
   - Acceptance criteria missing: Given, When, Then
   - Vague, hard-to-test wording: fast, quick, easy
[STORY-3] score 60 NEEDS WORK
   - Story is not in "As a <role>, I want <goal>, so that <benefit>" format
```

## Checking your own stories

Create a JSON file in the same shape as [sample_stories.json](sample_stories.json):

```json
[
  {
    "id": "STORY-1",
    "story": "As a program manager, I want to filter the dashboard by date, so that I can review a reporting period.",
    "acceptance_criteria": "Given I am on the dashboard\nWhen I select a date range\nThen only matching records are shown"
  }
]
```

Then run `python3 story_checker.py my_stories.json`.

## Using it with Claude Desktop (MCP)

1. Install the MCP library: `pip3 install -r requirements.txt`
2. In Claude Desktop, open **Settings > Developer > Edit Config** and add:

   ```json
   {
     "mcpServers": {
       "story-checker": {
         "command": "python3",
         "args": ["/FULL/PATH/TO/user-story-checker/server.py"]
       }
     }
   }
   ```

3. Restart Claude Desktop. Paste a story and ask: *"Check this story with story-checker."*

### Tools the server provides

| Tool | Input | Returns |
|---|---|---|
| `check_story` | `story` (text), `acceptance_criteria` (text, optional) | `score`, `ready`, `passes`, `problems` |
| `check_backlog` | `stories`: list of `{id, story, acceptance_criteria}` | `total`, `ready`, `average_score`, per-story `results` |

## Using the Claude skill

The skill in [skill/story-readiness/SKILL.md](skill/story-readiness/SKILL.md) is a step-by-step review procedure. To add it, upload the `story-readiness` folder as a custom skill in Claude (see Claude's help center for current steps). The skill works without the MCP server by applying the same checks by hand, and it uses the server's tools when they're connected.

## Project structure

```
user-story-checker/
├── story_checker.py            # scoring rules (no dependencies)
├── server.py                   # MCP server exposing the rules as tools
├── test_story_checker.py       # tests
├── sample_stories.json         # example input
├── requirements.txt            # mcp package
├── skill/story-readiness/
│   └── SKILL.md                # Claude skill: review procedure
├── docs/
│   ├── architecture.md         # how the pieces connect
│   └── scoring.md              # scoring rules in detail
├── .github/workflows/tests.yml # runs the tests on every push
├── CHANGELOG.md
└── LICENSE
```

## Limitations

- The checks are pattern-based. They confirm a story is *well-formed*, not that it's the *right* story. That judgment still belongs to the team and the Product Lead.
- The vague-word list is a starting set and will flag some legitimate uses (for example "quick filter" as a feature name).
- Format matching expects English and the standard "As a / I want / so that" wording.

## Roadmap

- [ ] Flag acceptance criteria with no measurable value (a number, a limit, a time)
- [ ] Read stories from a Jira CSV export
- [ ] Add INVEST checks (Independent, Negotiable, Valuable, Estimable, Small, Testable)

## Compatibility

Built with Python 3.13 and the `mcp` package 2.x; the tests run on Python 3.10 and 3.13. In `mcp` 1.x the server class was named `FastMCP` (`from mcp.server.fastmcp import FastMCP`); in 2.x it's `MCPServer`.

## Credits

Built by [Joshua Amponsah](https://linkedin.com/in/joshuaamponsah). The review standards come from my business analysis work. All code was run and tested before publishing.

## License

[MIT](LICENSE)
