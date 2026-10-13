"""Shared skill rules (skills-library R1 to R27) applied to each name in NEW_SKILLS.

A later skill feature adds its name to NEW_SKILLS (and DELIVERY_SKILLS) in conftest.py.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pytest
from conftest import (
    DELIVERY_SKILLS,
    NEW_SKILLS,
    REAL_SUPPORT_DIR,
    REPO,
    SKILLS_DIR,
    list_files,
    run_validator,
)

README = REPO / "README.md"
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
NEGATION = re.compile(r"\b(not|never|no|n't|without)\b", re.IGNORECASE)


def skill_text(name: str) -> str:
    path = SKILLS_DIR / name / "SKILL.md"
    assert path.is_file(), f"skills/{name}/SKILL.md does not exist"
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "no frontmatter"
    return match.group(1)


def paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


# R1
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_skill_exists_and_name_equals_folder(name: str) -> None:
    fm = frontmatter(skill_text(name))
    assert re.search(rf"^name:\s*{re.escape(name)}\s*$", fm, re.MULTILINE)


# R2
def test_validator_passes_on_all_skills() -> None:
    for name in NEW_SKILLS:
        skill_text(name)
    result = run_validator(SKILLS_DIR)
    assert result.returncode == 0, result.stdout + result.stderr


# R4
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_gets_data_through_base_skill_and_cli(name: str) -> None:
    text = skill_text(name)
    assert "`s1ft` skill" in text
    assert "s1ft meetings" in text


# R5
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_reads_data_files_directly_when_cli_cannot_run(name: str) -> None:
    lowered = skill_text(name).lower()
    assert re.search(r"cannot run|can't run|cannot be run|unable to run", lowered)
    assert "directly" in lowered


# R6
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_has_adapt_section(name: str) -> None:
    assert re.search(r"^## Adapt this skill\s*$", skill_text(name), re.MULTILINE)


# R7: allowed-tools names no write tool and runs only the s1ft CLI in Bash.
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_allowed_tools_has_no_write_tool(name: str) -> None:
    match = re.search(r"^allowed-tools:\s*(.+)$", frontmatter(skill_text(name)), re.MULTILINE)
    assert match, "no allowed-tools line"
    tokens = re.findall(r"[A-Za-z]+(?:\([^)]*\))?", match.group(1))
    assert tokens
    for token in tokens:
        assert token.split("(")[0] not in WRITE_TOOLS, token
        if token.startswith("Bash"):
            assert token == "Bash(s1ft:*)", f"Bash may run only the s1ft CLI: {token}"


# R8: no instruction to read transcript.md. A line may name it only to forbid it.
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_does_not_read_transcript_md(name: str) -> None:
    for line in skill_text(name).splitlines():
        if "transcript.md" in line:
            assert NEGATION.search(line), f"line tells the agent about transcript.md: {line!r}"


# R9: a meeting is read only through meeting.json or the CLI.
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_reads_meeting_only_through_meeting_json_or_cli(name: str) -> None:
    text = skill_text(name)
    assert "`meeting.json`" in text
    assert "s1ft meetings show" in text
    assert "history.json" not in text
    assert not re.search(r"\b(ls|find|cat)\s+\S*meetings?\b", text), "no shell listing of folders"


# R10: an empty result follows the rule of the base skill.
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_empty_result_uses_base_skill_rule(name: str) -> None:
    hits = [
        p
        for p in paragraphs(skill_text(name))
        if re.search(r"\bempty\b|no meetings", p, re.IGNORECASE) and "`s1ft` skill" in p
    ]
    assert hits, "no paragraph sends an empty result to the rule of the `s1ft` skill"


# R11: no path in the folder of another skill.
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_names_no_path_in_another_skill_folder(name: str) -> None:
    text = skill_text(name)
    others = [p.name for p in SKILLS_DIR.iterdir() if p.is_dir() and p.name != name]
    assert others
    for other in others:
        assert not re.search(rf"skills/{re.escape(other)}/", text), other
    assert "../" not in text


# R16
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_readme_table_lists_skill_with_one_sentence(name: str) -> None:
    rows = re.findall(
        rf"^\|\s*`{re.escape(name)}`\s*\|\s*(.+?)\s*\|\s*$",
        README.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    assert len(rows) == 1, f"README table needs exactly one row for `{name}`"
    sentence = rows[0]
    assert sentence.endswith("."), sentence
    assert not re.search(r"[.!?]\s+\S", sentence), f"more than one sentence: {sentence!r}"


# R22: a skill that reads a period reads one meeting at a time and keeps only its results.
@pytest.mark.parametrize("name", NEW_SKILLS)
def test_period_is_read_one_meeting_at_a_time(name: str) -> None:
    text = skill_text(name)
    lowered = text.lower()
    if "--since" not in text and "period" not in lowered:
        return
    assert "one meeting at a time" in lowered
    assert re.search(r"keep only|keep just", lowered)


# R27: the session fixture in conftest.py guards the real Application Support folder.
def test_real_support_dir_is_not_under_the_repo_or_a_temp_dir() -> None:
    assert REAL_SUPPORT_DIR.parts[-3:] == ("Library", "Application Support", "s1ft")
    assert not REAL_SUPPORT_DIR.is_relative_to(Path(tempfile.gettempdir()))


def test_list_files_sees_a_write(tmp_path: Path) -> None:
    root = tmp_path / "support"
    assert list_files(root) == []
    (root / "skills" / "summary").mkdir(parents=True)
    before = list_files(root)
    (root / "skills" / "summary" / "SKILL.md").write_text("x", encoding="utf-8")
    assert list_files(root) != before
    assert list_files(root) == [str(Path("skills") / "summary" / "SKILL.md")]


# R17 to R20: text rules of a delivery skill. DELIVERY_SKILLS is empty in this feature.
def delivery_violations(text: str) -> list[str]:
    """Return the rule ids that the text of a delivery skill breaks."""
    found: list[str] = []
    lowered = text.lower()
    if not re.search(r"\b(do not|does not|never) judge\b", lowered):
        found.append("R17: must say that it describes the data and does not judge")
    for line in text.splitlines():
        negated = bool(NEGATION.search(line))
        if re.search(r"\b(score|grade|rating|label)\b", line, re.IGNORECASE) and not negated:
            found.append(f"R18: gives a score, grade or label: {line.strip()!r}")
        if re.search(r"\b(ideal|perfect|optimal|target of)\b", line, re.IGNORECASE) and not negated:
            found.append(f"R19: states an ideal number: {line.strip()!r}")
    if not re.search(r"(do not|never|not) (comment|judge|give).*(other|another) speaker", lowered):
        found.append("R20: must forbid comments on the delivery of another speaker")
    return found


GOOD_DELIVERY = (
    "Describe the numbers. Do not judge the user.\n"
    "Never give a score, a grade or a label about the person.\n"
    "Do not state an ideal number as a rule.\n"
    "Do not comment on the delivery of another speaker.\n"
)


def test_delivery_checker_accepts_good_text() -> None:
    assert delivery_violations(GOOD_DELIVERY) == []


@pytest.mark.parametrize(
    ("bad", "rule"),
    [
        ("Give the user a score from 1 to 10.\n", "R18"),
        ("The ideal pace is 150 words per minute.\n", "R19"),
        ("Describe the numbers.\n", "R17"),
        ("Describe the numbers. Do not judge the user.\n", "R20"),
    ],
)
def test_delivery_checker_flags_bad_text(bad: str, rule: str) -> None:
    assert any(v.startswith(rule) for v in delivery_violations(bad))


@pytest.mark.parametrize("name", DELIVERY_SKILLS)
def test_delivery_skill_follows_text_rules(name: str) -> None:
    assert delivery_violations(skill_text(name)) == []
