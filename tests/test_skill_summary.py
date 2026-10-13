"""The `summary` skill (skills-library R29 to R35, R21, R31, R33).

`tests/fixtures/builtInSummary.txt` is the text of SkillStore.builtInSummary at a named commit
(see tests/fixtures/README.md).
"""

from __future__ import annotations

import re

import pytest
from conftest import FIXTURES, SKILLS_DIR

SKILL = SKILLS_DIR / "summary" / "SKILL.md"
FIXTURE = FIXTURES / "builtInSummary.txt"
ADAPT = re.compile(r"^## Adapt this skill\s*$", re.MULTILINE)
DATA_HEADING = re.compile(r"^## .*\bdata\b.*$", re.MULTILINE | re.IGNORECASE)


@pytest.fixture
def text() -> str:
    assert SKILL.is_file(), "skills/summary/SKILL.md does not exist"
    return SKILL.read_text(encoding="utf-8").replace("\r\n", "\n")


@pytest.fixture
def builtin() -> str:
    return FIXTURE.read_text(encoding="utf-8").strip("\n")


def frontmatter(text: str) -> str:
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "no frontmatter"
    return match.group(1)


def adapt_section(text: str) -> str:
    match = ADAPT.search(text)
    assert match, "no `## Adapt this skill` section"
    return text[match.end() :]


# Fixture sanity: the fixture carries the #204 text (passes without the skill).
def test_fixture_has_the_204_owner_rule_and_title_note(builtin: str) -> None:
    assert builtin.startswith("You are a meeting-notes assistant.")
    assert "listed attendee" in builtin
    assert "Never infer an owner from speaker labels" in builtin
    assert "calendar event title" in builtin
    assert "\\" not in builtin and "\t" not in builtin


# R1
def test_summary_exists_and_is_named_summary(text: str) -> None:
    assert re.search(r"^name:\s*summary\s*$", frontmatter(text), re.MULTILINE)


# R29: the built-in text, word for word, is in the body.
def test_body_holds_the_built_in_text_word_for_word(text: str, builtin: str) -> None:
    assert builtin in text


# R30
def test_includes_owner_rule_and_title_note(text: str) -> None:
    for phrase in [
        "Name an owner only when the transcript says explicitly who will do it AND that person "
        "is a listed attendee. Never infer an owner from speaker labels — they are unreliable.",
        "Meeting data: when the `meeting` data has a calendar event title, use that title for "
        "the top-level heading.",
    ]:
        assert phrase in text


# R31
def test_declares_uses_transcript_and_meeting(text: str) -> None:
    match = re.search(r'^\s+s1ft-uses:\s*"([^"]*)"\s*$', frontmatter(text), re.MULTILINE)
    assert match, "metadata.s1ft-uses must be a quoted comma string"
    assert [t.strip() for t in match.group(1).split(",")] == ["transcript", "meeting"]


# R32: data section, then the built-in text, then the Adapt section.
def test_data_section_then_built_in_text_then_adapt_section(text: str, builtin: str) -> None:
    body = text.split("\n---\n", 1)[1]
    data = DATA_HEADING.search(body)
    adapt = ADAPT.search(body)
    assert data, "no data section heading (a `## ... data` heading)"
    assert adapt, "no `## Adapt this skill` section"
    start = body.index(builtin)
    assert data.start() < start, "the data section must come before the built-in text"
    assert start + len(builtin) <= adapt.start(), "the Adapt section must come after the text"


# R33: the summary goes in the reply; summary.md is named only to forbid it.
def test_summary_is_given_in_the_reply_and_not_written(text: str) -> None:
    assert re.search(r"\b(in|as) (your|the) reply\b", text.lower())
    mentions = [line for line in text.splitlines() if "summary.md" in line]
    assert mentions, "the skill must name summary.md to forbid writing it"
    for line in mentions:
        assert re.search(r"\b(not|never|no)\b", line, re.IGNORECASE), line


# R21: a quote comes with the `start` time of the segment.
def test_quote_gives_the_start_time_of_the_segment(text: str) -> None:
    hits = [
        p
        for p in re.split(r"\n\s*\n", text)
        if re.search(r"\bquot", p, re.IGNORECASE) and "`start`" in p
    ]
    assert hits, "no paragraph says that a quote gives the `start` time of the segment"


# R34
def test_adapt_section_says_skill_change_does_not_change_the_app_summary(text: str) -> None:
    section = adapt_section(text)
    assert re.search(
        r"(change|edit)\w* (to|of|in) this skill[^.]*\b(does not|do not|doesn't)\b"
        r"[^.]*\bchange\b[^.]*\"?Summary\"?[^.]*\bapp\b",
        section,
        re.IGNORECASE,
    ), "Adapt section must say: a change to this skill does not change the \"Summary\" in the app"


# R35
def test_adapt_section_says_app_change_does_not_change_the_skill(text: str) -> None:
    section = adapt_section(text)
    assert re.search(
        r"(change|edit)\w* (in|of) the (s1ft )?app\b[^.]*\b(does not|do not|doesn't)\b"
        r"[^.]*\bchange\b[^.]*\bthis skill\b",
        section,
        re.IGNORECASE,
    ), "Adapt section must say: a change in the app does not change this skill"
