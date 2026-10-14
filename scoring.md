# Scoring rules

Every story is scored out of 100 across four checks.

## 1. Story format (40 points)

The story must match: **As a / As an** &lt;role&gt;**,** **I want** &lt;goal&gt;**, so that** &lt;benefit&gt;.

- Matching is case-insensitive.
- All three parts are required. A story without "so that" scores 0 here, because the benefit is what lets the team prioritise it.

## 2. Gherkin acceptance criteria (30 points)

The acceptance criteria are checked for the words **Given**, **When** and **Then**.

| Present | Points |
|---|---|
| All three | 30 |
| Two | 20 |
| One | 10 |
| None | 0 |

A story can't be marked Ready unless all three are present, whatever its total score.

## 3. Vague wording (20 points)

The story and acceptance criteria are checked for words that can't be tested:

`fast`, `quick`, `easy`, `simple`, `user-friendly`, `intuitive`, `etc`, `and/or`, `should be able`, `as needed`, `appropriate`, `robust`

Any match scores 0 for this check and lists the words found. The fix is to replace each one with something measurable. For example, "fast" becomes "loads in under 2 seconds".

The list is defined in `VAGUE_WORDS` in `story_checker.py` and is easy to extend.

## 4. Size (10 points)

Stories of 60 words or fewer get 10 points. Longer stories are flagged as candidates for splitting. Only the story text counts, not the acceptance criteria. The limit is `MAX_WORDS` in `story_checker.py`.

## Ready status

A story is **Ready** when:

- the total score is **80 or more**, and
- the acceptance criteria contain **Given, When and Then**.

## Examples

| Story | Score | Why |
|---|---|---|
| "As a program manager, I want to filter the dashboard by date range, so that I can review a reporting period." + full Given/When/Then | 100 | Passes everything |
| "As an analyst, I want the search to be fast and easy, so that I save time." + "Results should be quick." | 50 | No Gherkin; vague words |
| "Add an export button to the report page." + full Given/When/Then | 60 | Not in story format |
