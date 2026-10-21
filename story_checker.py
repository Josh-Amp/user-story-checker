"""
User story quality checker.

Scores an Agile user story against common quality checks:
- Uses the "As a <role>, I want <goal>, so that <benefit>" format
- Has at least one Gherkin acceptance criterion (Given / When / Then)
- Avoids vague words that make a story hard to test ("fast", "easy", ...)
- Isn't so long that it should probably be split

It also reviews the story the way a business analyst would: a one-line
verdict, an INVEST scorecard, findings for each part of the story (role,
want, benefit, acceptance criteria) and the habits to work on.

Run it directly to check the sample stories:
    python story_checker.py sample_stories.json
    python story_checker.py sample_stories.json --markdown   # full reviews
"""

import json
import re
import sys

# Words that make acceptance criteria hard to test. Each one should be
# replaced with something measurable ("loads in under 2 seconds").
VAGUE_WORDS = [
    "fast", "quick", "easy", "simple", "user-friendly", "intuitive",
    "etc", "and/or", "should be able", "as needed", "appropriate", "robust",
]

# Words that describe a fix with no finish line ("cleaned up", "improved").
# Only checked in the want and the acceptance criteria, because "so that I
# can make better decisions" is a fine benefit.
VAGUE_GOAL_PATTERNS = [
    r"clean(?:ed)?[ -]?up", r"streamlin(?:e|ed|ing)", r"improv(?:e|ed|ing)",
    r"better", r"enhanc(?:e|ed|ing)", r"optimi[sz](?:e|ed|ing)",
    r"seamless(?:ly)?", r"moderni[sz](?:e|ed)",
]

# Roles that don't say who the story is for.
GENERIC_ROLES = ["user", "users", "end user", "end-user", "someone", "somebody",
                 "anyone", "person", "people", "visitor"]

# Implementation terms. In the want they prescribe a solution; in acceptance
# criteria they describe plumbing a tester can't observe.
IMPLEMENTATION_TERMS = [
    "api", "endpoint", "database", "json", "sql", "schema", "server-side",
    "backend", "back-end", "frontend", "front-end", "component", "css", "html",
    "javascript", "webhook", "cache", "pipeline", "http", "query",
]

# Words that set scope by leaving things out. Worth a second look.
SCOPE_WORDS = ["only", "all", "every", "never", "always", "none"]

DEPENDENCY_PATTERN = re.compile(
    r"\b(?:depends on|dependent on|blocked by|prerequisite"
    r"|(?:after|once) .{1,40}? (?:is|are) (?:done|complete|built|released|live))\b",
    re.IGNORECASE,
)

STORY_PATTERN = re.compile(
    r"as an?\s+(?P<role>.+?),\s*i (?:want|need)\s+(?P<goal>.+?),?\s*"
    r"(?:so that|so i can|so we can|in order to)\s+(?P<benefit>.+)",
    re.IGNORECASE | re.DOTALL,
)

MAX_WORDS = 60  # a story longer than this is probably more than one story
MAX_SCENARIOS = 6  # more scenarios than this usually means two stories

STOPWORDS = {
    "that", "this", "with", "from", "have", "will", "would", "could", "should",
    "their", "they", "them", "then", "than", "into", "able", "want", "need",
    "when", "what", "which", "there", "here", "about", "more", "less", "some",
}

# The habits to work on, in the order a story gets written. Each finding
# points at one of these; a review lists the ones its findings touched.
TIPS = {
    "problem": "Start from the problem, not the fix. Write one sentence on what's wrong today and for whom before you write the story.",
    "role": 'Name a specific role, never "user". Use a persona you could interview. If the need is really yours, say "site owner" or "product owner".',
    "capability": "Make the want a capability. Describe what the person can do, not what the screen looks like, and drop words like cleaned up, streamlined or improved.",
    "benefit": 'Make "so that" add information. It should state the outcome or business value; if it repeats the want, ask "why does that matter?"',
    "observable": "Write criteria a stranger could test. Describe observable results in the user's words, not implementation terms such as API or JSON.",
    "unhappy": "Cover more than the happy path. Add at least one scenario for failure, empty data or permissions, and vary the Given to set it up.",
    "removals": 'Make removals explicit. If something goes away, name it in the story or a criterion; words like "only" and "all" deserve a second look.',
    "knock-on": "List the knock-on effects. Navigation, headings, copy, links and mobile layout are often touched by a change elsewhere.",
    "conversation": "Treat the card as a conversation starter (Card, Conversation, Confirmation). Write open questions under the story and resolve them before work starts.",
    "split": 'Split when criteria pile up. More than five or six scenarios, or "and" in the want, usually means two stories.',
}


def _finding(severity: str, label: str, detail: str, tip: str) -> dict:
    """severity is "problem" (blocks Ready) or "advice" (worth a look)."""
    return {"severity": severity, "label": label, "detail": detail, "tip": tip}


def _find_words(words: list[str], text: str) -> list[str]:
    return [w for w in words if re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", text, re.IGNORECASE)]


def _find_patterns(patterns: list[str], text: str) -> list[str]:
    found = []
    for p in patterns:
        m = re.search(rf"\b{p}\b", text, re.IGNORECASE)
        if m:
            found.append(m.group(0).lower())
    return found


def _content_words(text: str) -> set[str]:
    # First five letters as a cheap stem, so "filter" matches "filtering".
    return {w[:5] for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 4 and w not in STOPWORDS}


def _count_scenarios(acceptance_criteria: str) -> int:
    scenarios = len(re.findall(r"^\s*(?:[-*]\s*)?scenario\b", acceptance_criteria, re.IGNORECASE | re.MULTILINE))
    givens = len(re.findall(r"\bgiven\b", acceptance_criteria, re.IGNORECASE))
    return max(scenarios, givens)


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _quoted(words: list[str]) -> str:
    return _join([f'"{w}"' for w in words])


def check_story(story: str, acceptance_criteria: str = "") -> dict:
    """Check one story and return a score (0-100), passes, problems and a review."""
    passes, problems = [], []
    text = f"{story}\n{acceptance_criteria}"

    # 1. Story format (40 points)
    match = STORY_PATTERN.search(story)
    if match:
        passes.append(f"Story format OK (role: {match.group('role').strip()})")
    else:
        problems.append('Story is not in "As a <role>, I want <goal>, so that <benefit>" format')
    role = match.group("role").strip() if match else ""
    goal = match.group("goal").strip().rstrip(",") if match else ""
    benefit = match.group("benefit").strip().rstrip(".") if match else ""
    want_text = goal if match else story

    # 2. Gherkin acceptance criteria (30 points)
    has_given = re.search(r"\bgiven\b", acceptance_criteria, re.IGNORECASE)
    has_when = re.search(r"\bwhen\b", acceptance_criteria, re.IGNORECASE)
    has_then = re.search(r"\bthen\b", acceptance_criteria, re.IGNORECASE)
    missing = [w for w, found in (("Given", has_given), ("When", has_when), ("Then", has_then)) if not found]
    if not missing:
        passes.append("Acceptance criteria use Given / When / Then")
    else:
        problems.append(f"Acceptance criteria missing: {', '.join(missing)}")

    # 3. Vague words (20 points)
    vague_goal = _find_patterns(VAGUE_GOAL_PATTERNS, f"{want_text}\n{acceptance_criteria}")
    found_vague = _find_words(VAGUE_WORDS, text) + vague_goal
    vague_want = _find_words(VAGUE_WORDS, want_text) + _find_patterns(VAGUE_GOAL_PATTERNS, want_text)
    vague_ac = [w for w in found_vague if w not in vague_want and w in acceptance_criteria.lower()]
    if found_vague:
        problems.append(f"Vague, hard-to-test wording: {', '.join(found_vague)}")
    else:
        passes.append("No vague wording found")

    # 4. Size (10 points)
    word_count = len(story.split())
    if word_count > MAX_WORDS:
        problems.append(f"Story is {word_count} words; consider splitting it (limit {MAX_WORDS})")
    else:
        passes.append(f"Story size OK ({word_count} words)")

    score = (
        (40 if match else 0)
        + (30 if not missing else 10 * (3 - len(missing)))
        + (20 if not found_vague else 0)
        + (10 if word_count <= MAX_WORDS else 0)
    )

    # Part by part findings
    role_findings, want_findings, benefit_findings, ac_findings = [], [], [], []

    if not match:
        role_findings.append(_finding(
            "problem", "no role, want or benefit",
            'The story isn\'t in "As a <role>, I want <goal>, so that <benefit>" form, '
            "so nobody can say who it is for or why it matters.",
            "problem"))
    else:
        bare_role = re.sub(r"^(?:an?|the)\s+", "", role, flags=re.IGNORECASE).lower()
        if any(bare_role == g or bare_role.startswith(g + " ") for g in GENERIC_ROLES):
            role_findings.append(_finding(
                "advice", "the role is generic",
                'It doesn\'t say who this is for. The role decides what "valuable" means, '
                "so name a persona you could interview.",
                "role"))

    goal_impl = _find_words(IMPLEMENTATION_TERMS, want_text)
    if goal_impl:
        want_findings.append(_finding(
            "problem", "the want prescribes a solution",
            f"It names implementation ({', '.join(goal_impl)}) instead of a need, which leaves nothing to negotiate.",
            "capability"))
    if vague_want:
        want_findings.append(_finding(
            "problem", f"the want uses vague words ({', '.join(vague_want)})",
            "These are judgement words that describe a fix, not a capability. "
            "Say what the person can do afterwards that they can't do today.",
            "capability"))
    joined_want = bool(match and re.search(r"\band\b", goal, re.IGNORECASE))
    if joined_want:
        want_findings.append(_finding(
            "advice", "the want may be two stories",
            'Two wants joined by "and" are often two stories.',
            "split"))

    if match:
        goal_words, benefit_words = _content_words(goal), _content_words(benefit)
        if len(benefit_words) >= 2 and len(benefit_words & goal_words) / len(benefit_words) >= 0.6:
            benefit_findings.append(_finding(
                "advice", "the benefit repeats the want",
                'A good "so that" names the outcome the reader cares about, the reason the story is worth building.',
                "benefit"))

    if missing:
        ac_findings.append(_finding(
            "problem", "acceptance criteria aren't Given / When / Then",
            f"Missing {', '.join(missing)}, so there's no clear pass or fail.",
            "observable"))
    if vague_ac:
        ac_findings.append(_finding(
            "problem", f"criteria use vague words ({', '.join(vague_ac)})",
            f"{_quoted(vague_ac)} can't be verified. Replace each with something measurable, such as \"loads in under 2 seconds\".",
            "observable"))
    ac_impl = _find_words(IMPLEMENTATION_TERMS, acceptance_criteria)
    if ac_impl:
        ac_findings.append(_finding(
            "advice", "criteria describe implementation",
            f"{_quoted(ac_impl)} is plumbing a tester can't see. Describe what the person observes instead.",
            "observable"))
    scope = _find_words(SCOPE_WORDS, acceptance_criteria)
    if scope:
        ac_findings.append(_finding(
            "advice", f'"{scope[0]}" may hide scope',
            f"{_quoted(scope)} sets scope by leaving things out. If something is removed, name it.",
            "removals"))
    scenarios = _count_scenarios(acceptance_criteria)
    if not missing and scenarios == 1:
        ac_findings.append(_finding(
            "advice", "only the happy path is covered",
            "There's one scenario. Add one for failure, empty data or permissions.",
            "unhappy"))
    if scenarios > MAX_SCENARIOS:
        ac_findings.append(_finding(
            "advice", "too many scenarios",
            f"{scenarios} scenarios usually means more than one story.",
            "split"))

    parts = {
        "role": {"text": role, "findings": role_findings},
        "want": {"text": goal, "findings": want_findings},
        "benefit": {"text": benefit, "findings": benefit_findings},
        "acceptance_criteria": {"text": acceptance_criteria.strip(), "findings": ac_findings},
    }

    # INVEST scorecard. Each result is "pass", "fail" or "unclear". The checks
    # are pattern-based, so "unclear" means a person should take a look.
    def card(check, result, why):
        return {"check": check, "result": result, "why": why}

    dependency = DEPENDENCY_PATTERN.search(text)
    if dependency:
        independent = card("Independent", "unclear", f'It mentions a dependency ("{dependency.group(0)}"); check it can ship on its own.')
    else:
        independent = card("Independent", "pass", "No dependency on other work is mentioned.")

    if goal_impl:
        negotiable = card("Negotiable", "fail", f"The want prescribes the solution ({', '.join(goal_impl)}), leaving no room to discuss other ways to get the value.")
    else:
        negotiable = card("Negotiable", "pass", "The want doesn't name an implementation.")

    value_gaps = (["the role is generic"] if role_findings and match else []) + \
                 (["the benefit repeats the want"] if benefit_findings else [])
    if not match:
        valuable = card("Valuable", "fail", 'There\'s no "so that", so nobody can say who gains what.')
    elif value_gaps:
        valuable = card("Valuable", "unclear", f"{_join(value_gaps).capitalize()}, so it's hard to say who gains what.")
    else:
        valuable = card("Valuable", "pass", "A named role and a distinct benefit.")

    if vague_want:
        estimable = card("Estimable", "unclear", f"{_quoted(vague_want)} could mean anything from a small tweak to a redesign.")
    else:
        estimable = card("Estimable", "pass", "The want is specific enough to size.")

    if word_count > MAX_WORDS:
        small = card("Small", "fail", f"{word_count} words; stories over {MAX_WORDS} usually hide more than one story.")
    elif scenarios > MAX_SCENARIOS:
        small = card("Small", "fail", f"{scenarios} scenarios; over {MAX_SCENARIOS} usually means two stories.")
    elif joined_want:
        small = card("Small", "unclear", '"And" in the want may mean two stories.')
    else:
        small = card("Small", "pass", f"{word_count} words and {scenarios} scenario{'' if scenarios == 1 else 's'}.")

    if missing:
        testable = card("Testable", "fail", f"The acceptance criteria are missing {', '.join(missing)}.")
    elif found_vague:
        testable = card("Testable", "fail", f"{_quoted(found_vague)} {'has' if len(found_vague) == 1 else 'have'} no pass or fail.")
    elif ac_impl:
        testable = card("Testable", "unclear", f"The criteria name implementation ({', '.join(ac_impl)}) rather than what a tester observes.")
    else:
        testable = card("Testable", "pass", "Given / When / Then with observable results.")

    invest = [independent, negotiable, valuable, estimable, small, testable]
    ready = score >= 80 and not missing and not any(c["result"] == "fail" for c in invest)

    # Verdict: the answer first, with the main reasons
    findings = role_findings + want_findings + benefit_findings + ac_findings
    blocking = [f["label"] for f in findings if f["severity"] == "problem"]
    advice = [f["label"] for f in findings if f["severity"] == "advice"]
    if ready:
        verdict = "Ready for sprint planning."
        if advice:
            verdict += f" Worth a look first: {_join(advice)}."
    else:
        reasons = (blocking + advice)[:3] or [p[0].lower() + p[1:] for p in problems[:2]] or ["an INVEST check failed"]
        verdict = f"Not ready yet: {_join(reasons)}."

    # A story that isn't ready also gets the two habits no pattern can check.
    tip_keys = {f["tip"] for f in findings} | (set() if ready else {"knock-on", "conversation"})
    tips = [tip for key, tip in TIPS.items() if key in tip_keys]

    return {
        "score": score,
        "ready": ready,
        "verdict": verdict,
        "passes": passes,
        "problems": problems,
        "invest": invest,
        "parts": parts,
        "tips": tips,
    }


def check_backlog(stories: list[dict]) -> dict:
    """Check a list of {"id", "story", "acceptance_criteria"} items and summarise."""
    results = []
    for item in stories:
        result = check_story(item.get("story", ""), item.get("acceptance_criteria", ""))
        results.append({"id": item.get("id", "?"), **result})
    ready = sum(r["ready"] for r in results)
    avg = round(sum(r["score"] for r in results) / len(results), 1) if results else 0
    return {"total": len(results), "ready": ready, "average_score": avg, "results": results}


def review_markdown(story: str, acceptance_criteria: str = "", story_id: str = "") -> str:
    """Write a full review of one story as Markdown: the verdict, the story as
    submitted, an INVEST scorecard, part by part findings and habits to work on."""
    r = check_story(story, acceptance_criteria)
    lines = [f"# Story review{': ' + story_id if story_id else ''}", "", r["verdict"], "",
             "**The story as submitted**", "", f"> {story.strip()}"]
    for ac_line in acceptance_criteria.strip().splitlines():
        if ac_line.strip():
            lines += [">", f"> {ac_line.strip()}"]
    lines += ["", f"Score {r['score']}/100 · {'Ready' if r['ready'] else 'Needs work'}", ""]

    passed = sum(c["result"] == "pass" for c in r["invest"])
    lines += ["## Scorecard", "", f"It passes {passed} of the six INVEST checks.", "",
              "| Check | Result | Why |", "| --- | --- | --- |"]
    lines += [f"| {c['check']} | {c['result'].capitalize()} | {c['why']} |" for c in r["invest"]]

    lines += ["", "## Part by part", ""]
    for key, heading in (("role", "Role"), ("want", "Want"), ("benefit", "Benefit")):
        part = r["parts"][key]
        name = f'{heading}: "{part["text"]}."' if part["text"] else f"{heading}."
        body = " ".join(f["detail"] for f in part["findings"]) or "No issues found."
        lines += [f"**{name}** {body}", ""]
    ac = r["parts"]["acceptance_criteria"]["findings"]
    if ac:
        lines += ["**Acceptance criteria.**", ""]
        lines += [f"- **{f['label'][0].upper() + f['label'][1:]}.** {f['detail']}" for f in ac]
        lines.append("")
    else:
        lines += ["**Acceptance criteria.** No issues found.", ""]

    if r["tips"]:
        lines += ["## Going forward", ""]
        lines += [f"{i}. {tip}" for i, tip in enumerate(r["tips"], 1)]
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    with open(args[0] if args else "sample_stories.json") as f:
        stories = json.load(f)

    if "--markdown" in sys.argv:
        print("\n".join(
            review_markdown(s.get("story", ""), s.get("acceptance_criteria", ""), s.get("id", ""))
            for s in stories
        ))
        sys.exit(0)

    report = check_backlog(stories)
    print(f"{report['ready']} of {report['total']} stories ready | average score {report['average_score']}\n")
    for r in report["results"]:
        print(f"[{r['id']}] score {r['score']} {'READY' if r['ready'] else 'NEEDS WORK'}")
        print(f"   {r['verdict']}")
        print("   INVEST: " + " · ".join(f"{c['check']} {c['result']}" for c in r["invest"]))
        for p in r["problems"]:
            print(f"   - {p}")
