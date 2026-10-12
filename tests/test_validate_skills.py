"""AC 1-3 (and the pass case of AC 4) for scripts/validate_skills.py."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import VALIDATOR, good_frontmatter, run_validator, write_skill


def assert_rejected(skills_dir: Path, mention: str) -> None:
    assert VALIDATOR.is_file(), "scripts/validate_skills.py does not exist"
    result = run_validator(skills_dir)
    assert result.returncode == 1, result.stdout + result.stderr
    assert mention in result.stdout + result.stderr


def test_good_skill_passes(skills_dir: Path) -> None:
    write_skill(skills_dir, "demo", good_frontmatter())
    assert VALIDATOR.is_file(), "scripts/validate_skills.py does not exist"
    result = run_validator(skills_dir)
    assert result.returncode == 0, result.stdout + result.stderr


def test_all_standard_keys_pass(skills_dir: Path) -> None:
    frontmatter = (
        "name: demo\n"
        "description: Use when the user asks about a demo meeting.\n"
        "license: MIT\n"
        "compatibility: Needs the s1ft CLI.\n"
        "allowed-tools: Bash(s1ft:*) Read\n"
        "metadata:\n"
        '  s1ft-uses: "transcript,meeting,voice"\n'
        "  author: s1ft\n"
    )
    write_skill(skills_dir, "demo", frontmatter)
    assert VALIDATOR.is_file(), "scripts/validate_skills.py does not exist"
    assert run_validator(skills_dir).returncode == 0


@pytest.mark.parametrize(
    "uses", ["transcript", "meeting", "voice", "transcript,voice", "transcript, meeting, voice"]
)
def test_valid_s1ft_uses_values_pass(skills_dir: Path, uses: str) -> None:
    write_skill(skills_dir, "demo", good_frontmatter(uses=uses))
    assert VALIDATOR.is_file(), "scripts/validate_skills.py does not exist"
    result = run_validator(skills_dir)
    assert result.returncode == 0, result.stdout + result.stderr


def test_several_good_skills_pass(skills_dir: Path) -> None:
    write_skill(skills_dir, "one", good_frontmatter("one"))
    write_skill(skills_dir, "two", good_frontmatter("two", "voice"))
    assert VALIDATOR.is_file(), "scripts/validate_skills.py does not exist"
    assert run_validator(skills_dir).returncode == 0


# AC 1 (R189): only Agent Skills standard top-level keys.
@pytest.mark.parametrize("key", ["s1ft-uses", "version", "author", "tags", "uses"])
def test_non_standard_top_level_key_fails(skills_dir: Path, key: str) -> None:
    write_skill(skills_dir, "demo", good_frontmatter() + f"{key}: transcript\n")
    assert_rejected(skills_dir, key)


def test_metadata_must_be_a_map(skills_dir: Path) -> None:
    frontmatter = (
        "name: demo\n"
        "description: Use when the user asks about a demo meeting.\n"
        "metadata: transcript\n"
    )
    write_skill(skills_dir, "demo", frontmatter)
    assert_rejected(skills_dir, "metadata")


# AC 2 (R190): name equals folder name.
def test_name_differs_from_folder_fails(skills_dir: Path) -> None:
    write_skill(skills_dir, "demo", good_frontmatter(name="other"))
    assert_rejected(skills_dir, "name")


def test_name_check_is_per_skill(skills_dir: Path) -> None:
    write_skill(skills_dir, "one", good_frontmatter("one"))
    write_skill(skills_dir, "two", good_frontmatter("not-two"))
    assert_rejected(skills_dir, "two")


# AC 3 (R139, R187, R188): metadata.s1ft-uses is a comma list of known values.
def test_missing_metadata_fails(skills_dir: Path) -> None:
    frontmatter = "name: demo\ndescription: Use when the user asks about a demo meeting.\n"
    write_skill(skills_dir, "demo", frontmatter)
    assert_rejected(skills_dir, "s1ft-uses")


def test_metadata_without_s1ft_uses_fails(skills_dir: Path) -> None:
    frontmatter = (
        "name: demo\n"
        "description: Use when the user asks about a demo meeting.\n"
        "metadata:\n"
        "  author: s1ft\n"
    )
    write_skill(skills_dir, "demo", frontmatter)
    assert_rejected(skills_dir, "s1ft-uses")


@pytest.mark.parametrize(
    "uses",
    ["", "audio", "transcript, audio", "transcript;meeting", "transcript meeting", "Transcript"],
)
def test_bad_s1ft_uses_value_fails(skills_dir: Path, uses: str) -> None:
    write_skill(skills_dir, "demo", good_frontmatter(uses=uses))
    assert_rejected(skills_dir, "s1ft-uses")


def test_s1ft_uses_as_yaml_list_fails(skills_dir: Path) -> None:
    frontmatter = (
        "name: demo\n"
        "description: Use when the user asks about a demo meeting.\n"
        "metadata:\n"
        "  s1ft-uses:\n"
        "    - transcript\n"
        "    - meeting\n"
    )
    write_skill(skills_dir, "demo", frontmatter)
    assert_rejected(skills_dir, "s1ft-uses")


def test_one_bad_skill_fails_the_run(skills_dir: Path) -> None:
    write_skill(skills_dir, "good", good_frontmatter("good"))
    write_skill(skills_dir, "bad", good_frontmatter("bad", "audio"))
    assert_rejected(skills_dir, "bad")


def test_missing_frontmatter_fails(skills_dir: Path) -> None:
    folder = skills_dir / "demo"
    folder.mkdir()
    (folder / "SKILL.md").write_text("# No frontmatter\n", encoding="utf-8")
    assert_rejected(skills_dir, "demo")
