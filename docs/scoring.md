# Scoring rules

Every story is scored out of 100 across four checks, then reviewed with an INVEST scorecard and findings for each part of the story. Ready status depends on both.

## 1. Story format (40 points)

The story must match: **As a / As an** &lt;role&gt;**,** **I want** &lt;goal&gt;**, so that** &lt;benefit&gt;.

- Matching is case-insensitive. "I need" works as well as "I want", and "so I can", "so we can" or "in order to" work as well as "so that".
- All three parts are required. A story without a benefit scores 0 here, because the benefit is what lets the team prioritise it.

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

The want and the acceptance criteria are also checked for goals with no finish line:

`cleaned up`, `streamlined`, `improved`, `better`, `enhanced`, `optimized`, `seamless`, `modernized` (and their other forms)

These aren't checked in the benefit, because "so that I can make better decisions" is a fine benefit.

Any match scores 0 for this check and lists the words found. The fix is to replace each one with something measurable. For example, "fast" becomes "loads in under 2 seconds".

The lists are `VAGUE_WORDS` and `VAGUE_GOAL_PATTERNS` in `story_checker.py` and are easy to extend.

## 4. Size (10 points)

Stories of 60 words or fewer get 10 points. Longer stories are flagged as candidates for splitting. Only the story text counts, not the acceptance criteria. The limit is `MAX_WORDS` in `story_checker.py`.

## INVEST scorecard

Each check is **pass**, **fail** or **unclear**. The checks are pattern-based, so "unclear" means a person should look.

| Check | Fail when | Unclear when |
|---|---|---|
| Independent | | The story mentions a dependency ("depends on", "blocked by", "once … is done") |
| Negotiable | The want names an implementation (API, database, endpoint, component, pipeline…) | |
| Valuable | There's no benefit | The role is generic, or the benefit repeats the want |
| Estimable | | The want uses vague goal words (cleaned up, streamlined…) |
| Small | Over 60 words, or more than 6 scenarios | "And" joins two wants |
| Testable | Given / When / Then missing, or any vague word | The criteria use implementation terms (API, JSON…) |

The implementation terms are `IMPLEMENTATION_TERMS` in `story_checker.py`.

## Part by part findings

Each finding belongs to one part of the story and is either a **problem** (it goes with a failed check) or **advice** (worth a look, doesn't block Ready).

| Part | Finding | Severity |
|---|---|---|
| Role | Not in story format at all | problem |
| Role | Generic role: user, end user, someone, person, people, visitor | advice |
| Want | Names an implementation | problem |
| Want | Vague words | problem |
| Want | "And" joins two wants | advice |
| Benefit | 60% or more of its words (4+ letters) also appear in the want | advice |
| Acceptance criteria | Missing Given, When or Then | problem |
| Acceptance criteria | Vague words | problem |
| Acceptance criteria | Implementation terms | advice |
| Acceptance criteria | Scope words: only, all, every, never, always, none | advice |
| Acceptance criteria | One scenario, so no unhappy path | advice |
| Acceptance criteria | More than 6 scenarios | advice |

Scenarios are counted as the number of `Given` words or `Scenario:` lines, whichever is higher.

Each finding points to one item of the going-forward checklist (`TIPS` in `story_checker.py`). A review lists the items its findings touched. A story that isn't Ready also gets the two habits no pattern can check: listing knock-on effects and treating the card as a conversation starter.

## Ready status

A story is **Ready** when:

- the total score is **80 or more**,
- the acceptance criteria contain **Given, When and Then**, and
- **no INVEST check fails**.

Advice findings and "unclear" results don't block Ready, but they show up in the verdict as "worth a look first".

## Examples

| Story | Score | Why |
|---|---|---|
| "As a program manager, I want to filter the dashboard by date range, so that I can review a reporting period." + full Given/When/Then | 100 | Passes everything |
| "As an analyst, I want the search to be fast and easy, so that I save time." + "Results should be quick." | 50 | No Gherkin; vague words |
| "Add an export button to the report page." + full Given/When/Then | 60 | Not in story format |
| "As a user of the portfolio website, I want the Goals section to be cleaned up and streamlined so I can focus on the trailhead progress." + "Given I am on the portfolio website / When I navigate to the goals section / Then I should only see the live trailhead api" | 80, not Ready | Vague words fail Testable; generic role, "api" and "only" are flagged as advice |
