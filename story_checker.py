"""
User story quality checker.

Scores an Agile user story against common quality checks:
- Uses the "As a <role>, I want <goal>, so that <benefit>" format
- Has at least one Gherkin acceptance criterion (Given / When / Then)
- Avoids vague words that make a story hard to test ("fast", "easy", ...)
- Isn't so long that it should probably be split

Run it directly to check the sample stories:
    python story_checker.py sample_stories.json
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

STORY_PATTERN = re.compile(
    r"as an?\s+(?P<role>.+?),\s*i want\s+(?P<goal>.+?),?\s*so that\s+(?P<benefit>.+)",
    re.IGNORECASE | re.DOTALL,
)

MAX_WORDS = 60  # a story longer than this is probably more than one story


def check_story(story: str, acceptance_criteria: str = "") -> dict:
    """Check one story and return a score (0-100), passes and problems."""
    passes, problems = [], []
    text = f"{story}\n{acceptance_criteria}"

    # 1. Story format (40 points)
    match = STORY_PATTERN.search(story)
    if match:
        passes.append(f"Story format OK (role: {match.group('role').strip()})")
    else:
        problems.append('Story is not in "As a <role>, I want <goal>, so that <benefit>" format')

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
    found_vague = [w for w in VAGUE_WORDS if re.search(rf"\b{re.escape(w)}\b", text, re.IGNORECASE)]
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
    return {"score": score, "ready": score >= 80 and not missing, "passes": passes, "problems": problems}


def check_backlog(stories: list[dict]) -> dict:
    """Check a list of {"id", "story", "acceptance_criteria"} items and summarise."""
    results = []
    for item in stories:
        result = check_story(item.get("story", ""), item.get("acceptance_criteria", ""))
        results.append({"id": item.get("id", "?"), **result})
    ready = sum(r["ready"] for r in results)
    avg = round(sum(r["score"] for r in results) / len(results), 1) if results else 0
    return {"total": len(results), "ready": ready, "average_score": avg, "results": results}


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_stories.json"
    with open(path) as f:
        report = check_backlog(json.load(f))
    print(f"{report['ready']} of {report['total']} stories ready | average score {report['average_score']}\n")
    for r in report["results"]:
        print(f"[{r['id']}] score {r['score']} {'READY' if r['ready'] else 'NEEDS WORK'}")
        for p in r["problems"]:
            print(f"   - {p}")
