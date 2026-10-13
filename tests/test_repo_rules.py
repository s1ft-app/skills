"""Repo rules (skills-library R60 to R90): license, CONTRIBUTING, PR template, CI workflow.

All checks read text. Nothing runs the workflow or the network.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from conftest import REPO

LICENSE = REPO / "LICENSE"
README = REPO / "README.md"
CONTRIBUTING = REPO / "CONTRIBUTING.md"
TEMPLATE = REPO / ".github" / "pull_request_template.md"
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"
MANIFESTS = (REPO / ".claude-plugin" / "plugin.json", REPO / ".claude-plugin" / "marketplace.json")
DISCUSSIONS_URL = "github.com/s1ft-app/skills/discussions"
NUMBER_OF_SKILLS = re.compile(
    r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+"
    r"(\w+\s+)?(library\s+|data-access\s+)?skills?\b",
    re.IGNORECASE,
)


def read(path: Path) -> str:
    assert path.is_file(), f"{path.relative_to(REPO)} does not exist"
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"{path.relative_to(REPO)} is empty"
    return text


def need(text: str, pattern: str, message: str) -> None:
    assert re.search(pattern, text, re.IGNORECASE | re.DOTALL), message


def workflow_lines() -> list[str]:
    """Workflow lines without comments and blank lines."""
    lines = read(WORKFLOW).splitlines()
    return [ln for ln in lines if ln.strip() and not ln.lstrip().startswith("#")]


def top_level_block(key: str) -> str:
    """Text of a top-level key of the workflow (`on:`, `jobs:`) up to the next top-level key."""
    block: list[str] = []
    inside = False
    for line in workflow_lines():
        if re.match(r"^['\"]?[A-Za-z_-]+['\"]?:", line):
            inside = line.split(":", 1)[0].strip("'\"") == key
            if inside:
                block.append(line)
            continue
        if inside:
            block.append(line)
    assert block, f"workflow has no top-level `{key}:` block"
    return "\n".join(block)


def job_block(name: str) -> str:
    jobs = top_level_block("jobs").splitlines()[1:]
    block: list[str] = []
    inside = False
    for line in jobs:
        if re.match(r"^  [\w-]+:\s*$", line):
            inside = line.strip() == f"{name}:"
            continue
        if inside:
            block.append(line)
    assert block, f"workflow has no job `{name}`"
    return "\n".join(block)


# AC1 (R60, R76)
def test_license_is_apache_2() -> None:
    text = read(LICENSE)
    assert "Apache License" in text and "Version 2.0, January 2004" in text
    assert "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION" in text
    assert "END OF TERMS AND CONDITIONS" in text
    assert len(text.splitlines()) > 150, "LICENSE is too short for the full Apache 2.0 text"


# AC2 (R77)
def test_readme_names_license() -> None:
    need(
        read(README), r"Apache License,? (Version )?2\.0|Apache[- ]2\.0", "README names no license"
    )


# AC3 (R75)
def test_readme_links_contributing_and_discussions() -> None:
    text = read(README)
    need(text, r"\]\(\.?/?CONTRIBUTING\.md\)", "README has no link to CONTRIBUTING.md")
    assert DISCUSSIONS_URL in text, f"README has no link to {DISCUSSIONS_URL}"


# AC4 (R61, R62)
def test_contributing_idea_in_discussions_first() -> None:
    text = read(CONTRIBUTING)
    need(text, r"Discussions", "CONTRIBUTING does not mention Discussions")
    need(
        text,
        r"(idea|propos).{0,200}Discussions.{0,200}before.{0,80}pull request"
        r"|Discussions.{0,200}before.{0,120}pull request"
        r"|before.{0,80}pull request.{0,200}Discussions",
        "CONTRIBUTING must say: post an idea in Discussions before a pull request",
    )


# AC5 (R63)
def test_contributing_gives_validator_format_rules() -> None:
    text = read(CONTRIBUTING)
    assert "validate_skills.py" in text
    for key in ("name", "description", "metadata", "s1ft-uses"):
        assert f"`{key}`" in text, f"CONTRIBUTING gives no format rule for `{key}`"
    for use in ("transcript", "meeting", "voice"):
        assert use in text, f"CONTRIBUTING does not list the s1ft-uses value `{use}`"
    need(text, r"folder", "CONTRIBUTING does not say `name` equals the folder name")


# AC6 (R64)
def test_contributing_gives_commands() -> None:
    text = read(CONTRIBUTING)
    for command in (
        "scripts/validate_skills.py",
        "ruff check",
        "mypy",
        "pytest",
    ):
        assert command in text, f"CONTRIBUTING lacks the command `{command}`"


# AC7 (R65)
def test_contributing_gives_shared_skill_rules() -> None:
    text = read(CONTRIBUTING)
    # R17 to R20: the text rules for delivery skills
    need(text, r"judge", "R17: describe the data, do not judge")
    need(text, r"score|grade", "R18: no score, grade or label about the person")
    need(text, r"label", "R18: no label about the person")
    need(text, r"ideal", "R19: no ideal number as a rule")
    need(text, r"another speaker|other speaker", "R20: no comment on another speaker")
    # other shared rules in short form
    need(text, r"`?start`? time|start time", "R21: quote with the start time")
    need(text, r"one meeting at a time", "R22: read one meeting at a time")
    need(text, r"Application Support", "R27: tests never write the real s1ft data folder")
    need(text, r"Adapt this skill", "shared rule: Adapt this skill section")
    need(text, r"personal path|email address", "shared rule: no personal paths or emails")


# AC8 (R23, R24, R25)
def test_contributing_delivery_skill_needs_coach_review() -> None:
    text = read(CONTRIBUTING)
    assert "communication-coach" in text, "CONTRIBUTING does not name communication-coach"
    need(text, r"delivery skill", "CONTRIBUTING does not name the delivery skill")
    need(text, r"review.{0,60}comment|comment.{0,60}review", "no review comment rule")
    need(text, r"\bfix", "no fix rule for review results")
    need(text, r"reason", "no reason rule for review results")


# AC9 (R66)
def test_contributing_owner_decides_merge() -> None:
    need(
        read(CONTRIBUTING),
        r"owner.{0,80}decides?.{0,80}(merge|pull request)",
        "CONTRIBUTING must say the owner decides which pull request merges",
    )


# AC10 (R67)
def test_contributing_merged_skill_ships_in_plugin() -> None:
    need(
        read(CONTRIBUTING),
        r"merged skill.{0,120}plugin.{0,20}`s1ft`|plugin.{0,20}`s1ft`.{0,120}merged skill",
        "CONTRIBUTING must say a merged skill ships in the plugin `s1ft`",
    )


# AC11 (R78, R90)
def test_contributing_every_change_through_pull_request() -> None:
    need(
        read(CONTRIBUTING),
        r"(each|every) change.{0,80}owner.{0,120}pull request"
        r"|owner.{0,80}(each|every) change.{0,120}pull request",
        "CONTRIBUTING must say each change, also from the owner, comes through a pull request",
    )


# AC12 (R84)
def test_contributing_owner_merges_after_required_checks() -> None:
    need(
        read(CONTRIBUTING),
        r"owner.{0,60}merges?.{0,60}only after.{0,60}(required )?checks.{0,20}pass",
        "CONTRIBUTING must say the owner merges only after the required checks pass",
    )


# AC13 (R68, R69)
def test_template_has_six_check_items() -> None:
    text = read(TEMPLATE)
    items = re.findall(r"^\s*[-*]\s*\[[ xX]\]\s*(.+)$", text, re.MULTILINE)
    assert len(items) == 6, f"template has {len(items)} check items, expected 6"
    expected = (
        r"validator",
        r"tests",
        r"Adapt this skill",
        r"base skill|`s1ft` skill",
        r"personal path|email",
        r"describes?.{0,20}(does not|doesn't|and not|not) judge|judge",
    )
    for pattern, item in zip(expected, items, strict=True):
        need(item, pattern, f"check item does not match /{pattern}/: {item}")


# AC14 (R70, R71)
def test_workflow_runs_on_pull_request_and_push_to_main() -> None:
    trigger = top_level_block("on")
    assert re.search(r"\bpull_request\b", trigger), "workflow has no pull_request trigger"
    assert re.search(r"\bpush\b", trigger), "workflow has no push trigger"
    need(trigger, r"push:.*branches:.*\bmain\b", "push trigger must be limited to main")
    assert "pull_request_target" not in trigger, "pull_request_target runs with secrets"


def test_workflow_has_job_checks() -> None:
    assert "run" in job_block("checks") or "steps" in job_block("checks")
    assert "runs-on" in job_block("checks")


# AC15 (R70)
def test_workflow_runs_all_four_checks() -> None:
    steps = job_block("checks")
    assert "scripts/validate_skills.py" in steps, "job checks does not run the validator"
    assert re.search(r"\bruff check\b", steps), "job checks does not run ruff"
    assert re.search(r"\bmypy\b", steps), "job checks does not run mypy"
    assert re.search(r"\bpytest\b", steps), "job checks does not run pytest"
    need(steps, r"-m\s+['\"]not network['\"]", 'job checks must run pytest -m "not network"')


def test_workflow_network_job_only_on_push() -> None:
    block = job_block("network")
    assert re.search(r"pytest.*-m\s+['\"]?network", block), "network job must run pytest -m network"
    need(block, r"if:.*push", "network job must run only on push to main")
    assert "checks" not in re.findall(r"needs:\s*(\S+)", block)


# AC16 (R72)
def test_workflow_uses_no_secrets() -> None:
    text = read(WORKFLOW)
    assert "secrets." not in text, "workflow uses a secrets. value"
    assert "secrets:" not in text and "secrets[" not in text
    assert "GITHUB_TOKEN" not in text, "workflow needs no token"


# AC17 (R73): text check only. No run happens here.
def test_workflow_needs_no_claude_command() -> None:
    for line in workflow_lines():
        assert not re.search(r"\bclaude\b", line, re.IGNORECASE), (
            f"workflow mentions claude (the runner has no claude command): {line.strip()}"
        )
    assert "npm install" not in read(WORKFLOW) and "npx" not in job_block("checks")


# AC18 (R15)
def test_manifest_descriptions_state_no_skill_count() -> None:
    descriptions: list[str] = []
    for path in MANIFESTS:
        data = json.loads(path.read_text(encoding="utf-8"))
        descriptions.append(data["description"])
        descriptions.extend(entry["description"] for entry in data.get("plugins", []))
    assert len(descriptions) == 3, (
        "expected 3 descriptions (plugin, marketplace, marketplace entry)"
    )
    for description in descriptions:
        assert description.strip()
        assert not NUMBER_OF_SKILLS.search(description), f"description counts skills: {description}"


def test_skill_count_check_catches_numbers() -> None:
    for bad in ("plus six library skills", "All seven skills", "7 skills", "one skill"):
        assert NUMBER_OF_SKILLS.search(bad), bad
    assert not NUMBER_OF_SKILLS.search("Agent skills for s1ft meeting data.")
