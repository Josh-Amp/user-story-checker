# User Story Checker

**A user story quality checker for Agile teams, available to AI assistants through an MCP server and a Claude skill.**

[![tests](https://github.com/Josh-Amp/user-story-checker/actions/workflows/tests.yml/badge.svg)](https://github.com/Josh-Amp/user-story-checker/actions/workflows/tests.yml)

Story Checker scores user stories for sprint readiness and reviews them the way a business analyst would. It checks whether each story uses the standard format, has testable Gherkin acceptance criteria, avoids vague wording, and is small enough for one sprint. Then it writes a review: a one-line verdict, an INVEST scorecard, findings for each part of the story, and the habits the writer should work on. You can run it as a plain Python script, or connect it to an AI assistant such as Claude Desktop so the assistant can check a whole backlog during grooming.

## Why I built it

As a business analyst I have written 150+ Jira tickets, including user stories with Gherkin acceptance criteria. Most rework I saw came from stories that weren't ready: missing "so that" benefits, acceptance criteria with no Given / When / Then, and words like "fast" or "easy" that nobody can test. This project turns those review standards into code. It's also a hands-on way to learn how AI tools are built, through MCP (Model Context Protocol) and Claude skills.

## What it checks

| Check | Points | Why it matters |
|---|---|---|
| "As a &lt;role&gt;, I want &lt;goal&gt;, so that &lt;benefit&gt;" format | 40 | Makes the user and the value explicit |
| Gherkin acceptance criteria (Given / When / Then) | 30 | Gives developers and testers a clear pass/fail test |
| No vague, untestable words (fast, easy, intuitive, etc.) | 20 | Vague words can't be verified in QA |
| Story is 60 words or fewer | 10 | Long stories usually hide more than one story |

A story is **Ready** when it scores 80 or more, its acceptance criteria include all of Given, When and Then, **and** none of its INVEST checks fail. See [docs/scoring.md](docs/scoring.md) for the full rules.

## The review

The score says whether a story is well-formed. The review says what to fix and why, in the same order every time:

| Section | What it gives you |
|---|---|
| Verdict | One sentence up front: ready or not, and the main reasons |
| The story as submitted | The story and its acceptance criteria, quoted |
| Scorecard | The six INVEST checks (Independent, Negotiable, Valuable, Estimable, Small, Testable), each **pass**, **fail** or **unclear** with a one-line reason |
| Part by part | Findings for the role, the want, the benefit and the acceptance criteria |
| Going forward | The habits this story showed it needs, from a 10-point checklist |

Part by part, the checker looks for:

| Part | Flags |
|---|---|
| Role | Generic roles such as "a user" or "a visitor" |
| Want | Implementation terms (API, database, component); vague goals with no finish line (cleaned up, streamlined, improved); "and" joining two wants |
| Benefit | A "so that" that repeats the want instead of naming the value |
| Acceptance criteria | Missing Given / When / Then; vague words; implementation terms a tester can't observe; "only" or "all" hiding a removal; a single happy-path scenario; more than six scenarios |

Findings are either **problems**, which stop a story being Ready, or **advice**, which is worth a look but doesn't block it.

The Claude skill adds what a pattern check can't: a rewrite with full acceptance criteria, notes for the conversation and open questions for the Product Lead. See [Using the Claude skill](#using-the-claude-skill).

## How it fits together

```
 You (in Claude Desktop)
        │  "Are these stories ready for sprint planning?"
        ▼
 Claude  ── follows ──▶  skill/story-readiness/SKILL.md   (the review procedure)
        │
        │  calls tools over MCP (stdin/stdout)
        ▼
 server.py  (MCP server: check_story, check_backlog, review_story)
        │
        ▼
 story_checker.py  (the scoring rules, plain Python)
```

- **`story_checker.py`** holds the rules and writes the review. It has no dependencies and runs on its own.
- **`server.py`** wraps those rules as three MCP tools so any MCP-compatible AI app can call them.
- **`SKILL.md`** tells Claude *how* to run a readiness review: collect stories, call the tools, look at the real product, and write the review in the format above with a rewrite and open questions for the Product Lead.

More detail is in [docs/architecture.md](docs/architecture.md).

## Quick start

Requires Python 3.10 or newer.

```bash
git clone https://github.com/Josh-Amp/user-story-checker.git
cd user-story-checker

# 1. Check the sample stories (no install needed)
python3 story_checker.py sample_stories.json

# 2. Write a full review of each story
python3 story_checker.py sample_stories.json --markdown

# 3. Run the tests
python3 test_story_checker.py
```

Example output (trimmed to two stories):

```
1 of 4 stories ready | average score 72.5

[STORY-1] score 100 READY
   Ready for sprint planning. Worth a look first: "only" may hide scope and only the happy path is covered.
   INVEST: Independent pass · Negotiable pass · Valuable pass · Estimable pass · Small pass · Testable pass
[STORY-4] score 80 NEEDS WORK
   Not ready yet: the want uses vague words (cleaned up, streamlined), the role is generic and the want may be two stories.
   INVEST: Independent pass · Negotiable pass · Valuable unclear · Estimable unclear · Small unclear · Testable fail
   - Vague, hard-to-test wording: cleaned up, streamlined
```

STORY-4 scores 80 but still isn't Ready, because its Testable check fails. With `--markdown`, the same story gets a full review:

```markdown
# Story review: STORY-4

Not ready yet: the want uses vague words (cleaned up, streamlined), the role is generic and the want may be two stories.

## Scorecard

It passes 2 of the six INVEST checks.

| Check | Result | Why |
| --- | --- | --- |
| Valuable | Unclear | The role is generic, so it's hard to say who gains what. |
| Testable | Fail | "cleaned up" and "streamlined" have no pass or fail. |
...

## Part by part

**Role: "user of the portfolio website."** It doesn't say who this is for. ...

**Acceptance criteria.**

- **Criteria describe implementation.** "api" is plumbing a tester can't see. ...
- **"only" may hide scope.** "only" sets scope by leaving things out. If something is removed, name it.
- **Only the happy path is covered.** There's one scenario. Add one for failure, empty data or permissions.

## Going forward

1. Name a specific role, never "user". ...
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

Then run `python3 story_checker.py my_stories.json`, or add `--markdown` for full reviews. Each `Given` (or `Scenario:` line) in the acceptance criteria counts as one scenario.

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

3. Restart Claude Desktop. Paste a story and ask: *"Check this story with story-checker."* or *"Review this story."*

### Tools the server provides

| Tool | Input | Returns |
|---|---|---|
| `check_story` | `story` (text), `acceptance_criteria` (text, optional) | `score`, `ready`, `verdict`, `passes`, `problems`, `invest`, `parts`, `tips` |
| `check_backlog` | `stories`: list of `{id, story, acceptance_criteria}` | `total`, `ready`, `average_score`, per-story `results` (each shaped like `check_story`) |
| `review_story` | `story`, `acceptance_criteria` (optional), `story_id` (optional) | The full review as Markdown |

`invest` is a list of `{check, result, why}`. `parts` has `role`, `want`, `benefit` and `acceptance_criteria`, each with the `text` found and a list of `findings` (`severity`, `label`, `detail`, `tip`). `tips` is the going-forward checklist for that story.

## Using the Claude skill

The skill in [skill/story-readiness/SKILL.md](skill/story-readiness/SKILL.md) is a step-by-step review procedure. It has Claude write every review in the same format as the tool, then add the parts that need judgment:

1. **Verdict**, the answer first
2. **The story as submitted**
3. **Scorecard** of the INVEST checks, confirming or overruling the tool's pattern-based results
4. **Part by part** findings for the role, want, benefit and acceptance criteria, grounded in the real product when Claude can see it
5. **A rewrite** with numbered Given / When / Then criteria, including an unhappy path and knock-on changes
6. **Notes for the conversation**
7. **Going forward** checklist
8. **Open questions** for the Product Lead

To add it, upload the `story-readiness` folder as a custom skill in Claude (see Claude's help center for current steps). The skill works without the MCP server by applying the same checks by hand, and it uses the server's tools when they're connected.

## Project structure

```
user-story-checker/
├── story_checker.py            # scoring rules and review (no dependencies)
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
- INVEST results are heuristics. "Unclear" means a person should look, and a "pass" on Independent only means no dependency was mentioned. The skill asks Claude to confirm or overrule each one.
- "The benefit repeats the want" compares words, so it catches "export reports so that I can export reports" but not a benefit that restates the want in different words.
- The vague-word list is a starting set and will flag some legitimate uses (for example "quick filter" as a feature name, or "only" in "only matching records are shown").
- Format matching expects English and the standard "As a / I want / so that" wording.

## Roadmap

- [ ] Flag acceptance criteria with no measurable value (a number, a limit, a time)
- [ ] Read stories from a Jira CSV export
- [x] Add INVEST checks (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- [ ] Flag knock-on effects (navigation, headings, copy) when a story removes something

## Compatibility

Built with Python 3.13 and the `mcp` package 2.x; the tests run on Python 3.10 and 3.13. In `mcp` 1.x the server class was named `FastMCP` (`from mcp.server.fastmcp import FastMCP`); in 2.x it's `MCPServer`.

## Credits

Built by [Joshua Amponsah](https://linkedin.com/in/joshuaamponsah). The review standards come from my business analysis work. All code was run and tested before publishing.

## License

[MIT](LICENSE)
