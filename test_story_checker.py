"""Tests for the story checker. Run: python -m pytest  (or python test_story_checker.py)"""

from story_checker import check_backlog, check_story

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


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
