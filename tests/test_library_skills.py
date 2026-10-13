"""R138-R141, R190: the six library skills exist, validate and follow the shared rules."""

from __future__ import annotations

import re

import pytest
from conftest import NEW_SKILLS, REPO, run_validator

SIX_LIBRARY_SKILLS = [
    "follow-up-email",
    "decision-log",
    "action-items",
    "review-my-delivery",
    "meeting-type",
    "weekly-trends",
]
# skills-library R3: each new skill passes the tests that apply to all library skills.
LIBRARY = [*SIX_LIBRARY_SKILLS, *NEW_SKILLS]
VOICE_SKILLS = ["review-my-delivery", "weekly-trends"]
SKILLS = REPO / "skills"


def read(name: str) -> str:
    path = SKILLS / name / "SKILL.md"
    assert path.is_file(), f"skills/{name}/SKILL.md does not exist"
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "no frontmatter"
    return match.group(1)


@pytest.mark.parametrize("name", LIBRARY)
def test_skill_exists_and_name_equals_folder(name: str) -> None:
    assert re.search(rf"^name:\s*{re.escape(name)}\s*$", frontmatter(read(name)), re.MULTILINE)


def test_validator_passes_on_all_skills() -> None:
    for name in LIBRARY:
        read(name)
    result = run_validator(SKILLS)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("name", LIBRARY)
def test_declares_uses_as_comma_string(name: str) -> None:
    match = re.search(r'^\s+s1ft-uses:\s*"([a-z, ]+)"\s*$', frontmatter(read(name)), re.MULTILINE)
    assert match, "metadata.s1ft-uses must be a quoted comma string"


@pytest.mark.parametrize("name", VOICE_SKILLS)
def test_voice_skills_declare_voice(name: str) -> None:
    assert "voice" in frontmatter(read(name))


@pytest.mark.parametrize("name", LIBRARY)
def test_relies_on_base_skill_and_cli_with_fallback(name: str) -> None:
    text = read(name)
    assert "`s1ft` skill" in text
    assert "s1ft meetings" in text
    assert re.search(r"directly|data files", text.lower())


@pytest.mark.parametrize("name", LIBRARY)
def test_has_adapt_section(name: str) -> None:
    assert re.search(r"^## Adapt this skill\s*$", read(name), re.MULTILINE)


@pytest.mark.parametrize("name", LIBRARY)
def test_no_personal_paths_or_emails(name: str) -> None:
    text = read(name)
    assert "/Users/" not in text
    assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text.replace("name@example.com", ""))


@pytest.mark.parametrize("name", LIBRARY)
def test_does_not_duplicate_cli_docs(name: str) -> None:
    text = read(name)
    assert "ln -sf" not in text
    assert "schemaVersion" not in text


@pytest.mark.parametrize("name", VOICE_SKILLS)
def test_voice_skills_use_voice_stats_defaults(name: str) -> None:
    text = read(name)
    assert "s1ft voice stats" in text
    for token in ["-50", "300", "p10"]:
        assert token in text


def test_follow_up_email_needs_external_attendees() -> None:
    text = read("follow-up-email").lower()
    assert "external" in text
    assert "attendees" in text
    assert "stop" in text


def test_review_my_delivery_covers_interpretation_and_tone() -> None:
    text = read("review-my-delivery").lower()
    for word in ["pauses", "pace", "uptalk", "fillers", "interruptions"]:
        assert word in text


def test_weekly_trends_compares_weeks() -> None:
    text = read("weekly-trends").lower()
    assert "--since" in text
    assert "week" in text
    assert "trend" in text


def test_meeting_type_lists_types() -> None:
    text = read("meeting-type").lower()
    for word in ["one-on-one", "standup", "client"]:
        assert word in text
