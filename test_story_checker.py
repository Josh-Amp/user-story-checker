"""Tests for the story checker. Run: python -m pytest  (or python test_story_checker.py)"""

import zipfile
from pathlib import Path

from story_checker import check_backlog, check_story, review_markdown

GOOD_STORY = "As a reviewer, I want to see flagged records, so that I can fix data errors."
GOOD_AC = "Given a record has a missing field\nWhen I open the review queue\nThen the record is listed"


def test_good_story_is_ready():
    result = check_story(GOOD_STORY, GOOD_AC)
    assert result["score"] == 100
    assert result["ready"]


def test_wrong_format_is_flagged():
    result = check_story("Add an export button.", GOOD_AC)
    assert not result["ready"]
    assert any("format" in p for p in result["problems"])


def test_vague_words_are_flagged():
    result = check_story("As a user, I want it fast, so that I save time.", GOOD_AC)
    assert any("fast" in p for p in result["problems"])


def test_missing_gherkin_is_flagged():
    result = check_story(GOOD_STORY, "It works.")
    assert not result["ready"]
    assert any("Given, When, Then" in p for p in result["problems"])


def test_backlog_summary():
    report = check_backlog([
        {"id": "A", "story": GOOD_STORY, "acceptance_criteria": GOOD_AC},
        {"id": "B", "story": "Fix it.", "acceptance_criteria": ""},
    ])
    assert report["total"] == 2
    assert report["ready"] == 1


GOALS_STORY = ("As a user of the portfolio website, I want the Goals section to be cleaned up "
               "and streamlined so I can focus on the trailhead progress.")
GOALS_AC = ("Given I am on the portfolio website\nWhen I navigate to the goals section\n"
            "Then I should only see the live trailhead api")


def invest(result):
    return {c["check"]: c["result"] for c in result["invest"]}


def labels(result, part):
    return [f["label"] for f in result["parts"][part]["findings"]]


def test_good_story_passes_invest():
    result = check_story(GOOD_STORY, GOOD_AC)
    assert set(invest(result).values()) == {"pass"}
    assert result["verdict"].startswith("Ready")


def test_so_i_can_counts_as_a_benefit():
    result = check_story("As a reviewer, I want to see flagged records so I can fix data errors.", GOOD_AC)
    assert result["parts"]["benefit"]["text"] == "fix data errors"


def test_goals_story_review():
    result = check_story(GOALS_STORY, GOALS_AC)
    assert not result["ready"]
    assert "the role is generic" in labels(result, "role")
    assert any("cleaned up" in label for label in labels(result, "want"))
    ac = labels(result, "acceptance_criteria")
    assert "criteria describe implementation" in ac
    assert '"only" may hide scope' in ac
    assert "only the happy path is covered" in ac
    assert invest(result)["Testable"] == "fail"
    assert invest(result)["Valuable"] == "unclear"


def test_implementation_in_want_fails_negotiable():
    result = check_story("As a recruiter, I want a JSON endpoint for badges, so that I can verify skills.", GOOD_AC)
    assert invest(result)["Negotiable"] == "fail"
    assert not result["ready"]


def test_benefit_that_repeats_the_want():
    result = check_story("As a manager, I want to export reports, so that I can export reports.", GOOD_AC)
    assert "the benefit repeats the want" in labels(result, "benefit")


def test_better_is_fine_in_the_benefit():
    result = check_story("As a manager, I want to filter reports by region, so that I make better decisions.", GOOD_AC)
    assert result["ready"]


def test_two_scenarios_cover_the_unhappy_path():
    ac = GOOD_AC + "\n\nGiven the queue is empty\nWhen I open the review queue\nThen I see a message"
    result = check_story(GOOD_STORY, ac)
    assert "only the happy path is covered" not in labels(result, "acceptance_criteria")


def test_markdown_review_sections():
    md = review_markdown(GOALS_STORY, GOALS_AC, "STORY-4")
    for heading in ("# Story review: STORY-4", "## Scorecard", "## Part by part", "## Going forward"):
        assert heading in md
    assert "| Testable | Fail |" in md


def test_skill_zip_matches_skill_folder():
    root = Path(__file__).parent
    with zipfile.ZipFile(root / "story-readiness.zip") as z:
        zipped = z.read("story-readiness/SKILL.md")
    assert zipped == (root / "skill" / "story-readiness" / "SKILL.md").read_bytes(), \
        "story-readiness.zip is out of date; rebuild it from the skill folder"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
