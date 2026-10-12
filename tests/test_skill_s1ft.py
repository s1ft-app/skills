"""AC 4-11: the base skill skills/s1ft/SKILL.md."""

from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import BASE_SKILL, REPO, VALIDATOR, run_validator

APP_HELPER = "/Applications/S1ft.app/Contents/Helpers/s1ft"
LINK = "~/.local/bin/s1ft"


@pytest.fixture
def skill_text() -> str:
    assert BASE_SKILL.is_file(), "skills/s1ft/SKILL.md does not exist"
    return BASE_SKILL.read_text(encoding="utf-8")


def has_all(text: str, words: list[str]) -> list[str]:
    lowered = text.lower()
    return [w for w in words if w.lower() not in lowered]


# AC 4 (R78, R79)
def test_base_skill_exists_in_skill_md_format(skill_text: str) -> None:
    assert skill_text.startswith("---\n")
    assert re.search(r"^name:\s*s1ft\s*$", skill_text, re.MULTILINE)
    assert re.search(r"^description:\s*\S", skill_text, re.MULTILINE)


def test_validator_passes_on_repo_skills() -> None:
    assert VALIDATOR.is_file(), "scripts/validate_skills.py does not exist"
    assert BASE_SKILL.is_file(), "skills/s1ft/SKILL.md does not exist"
    result = run_validator(REPO / "skills")
    assert result.returncode == 0, result.stdout + result.stderr


def test_validator_default_run_is_green() -> None:
    """The issue's test strategy: `python3 scripts/validate_skills.py` with no argument."""
    assert VALIDATOR.is_file(), "scripts/validate_skills.py does not exist"
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# AC 5 (R80)
def test_describes_meeting_folder_and_data_files(skill_text: str) -> None:
    missing = has_all(
        skill_text,
        ["meeting folder", "meeting.json", "transcript.json", "telemetry.json", "schemaVersion"],
    )
    assert not missing, missing


def test_describes_meeting_json_schema(skill_text: str) -> None:
    fields = [
        "id",
        "name",
        "platform",
        "start",
        "end",
        "calendarEvents",
        "title",
        "isAllDay",
        "attendees",
        "email",
        "usedForName",
    ]
    missing = [f for f in fields if f"`{f}`" not in skill_text]
    assert not missing, missing


def test_describes_transcript_json_schema(skill_text: str) -> None:
    missing = [
        f for f in ["segments", "speaker", "start", "end", "text"] if f"`{f}`" not in skill_text
    ]
    assert not missing, missing


def test_describes_telemetry_json_schema(skill_text: str) -> None:
    fields = ["source", "method", "sampleRateHz", "spans", "pitchHz", "rmsDbfs", "peakDbfs"]
    missing = [f for f in fields if f"`{f}`" not in skill_text]
    assert not missing, missing


def test_names_each_cli_command(skill_text: str) -> None:
    commands = [
        "s1ft meetings list",
        "s1ft meetings search",
        "s1ft meetings show",
        "s1ft voice stats",
        "s1ft --version",
    ]
    missing = [c for c in commands if c not in skill_text]
    assert not missing, missing


def test_names_cli_options(skill_text: str) -> None:
    missing = [o for o in ["--json", "--since", "--until", "--dir"] if o not in skill_text]
    assert not missing, missing


# AC 6 (R81)
def test_has_interpretation_guidance(skill_text: str) -> None:
    missing = has_all(skill_text, ["pauses", "pace", "uptalk", "fillers", "interruptions"])
    assert not missing, missing


# AC 7 (R82)
def test_version_check_and_stop(skill_text: str) -> None:
    lowered = skill_text.lower()
    assert "s1ft --version" in skill_text
    assert "incompatible" in lowered
    assert "stop" in lowered


# AC 8 (R83)
def test_fallback_reads_data_files_directly(skill_text: str) -> None:
    lowered = skill_text.lower()
    assert "directly" in lowered
    assert re.search(r"cannot run|can't run|cannot be run|unable to run|not installed", lowered)


# AC 9 (R168)
def test_install_step_links_cli(skill_text: str) -> None:
    assert LINK in skill_text
    assert APP_HELPER in skill_text
    assert link_lines(skill_text), "no `ln` command in a fenced shell block"


def link_lines(text: str) -> list[str]:
    """Lines of fenced sh/bash blocks that make the link: `mkdir` and `ln` commands."""
    lines: list[str] = []
    for block in re.findall(r"```(?:bash|sh|zsh|shell)\n(.*?)```", text, re.DOTALL):
        for line in block.splitlines():
            stripped = line.strip().lstrip("$ ").strip()
            if re.match(r"(mkdir|ln)\s", stripped):
                lines.append(stripped)
    return lines if any(line.startswith("ln ") for line in lines) else []


# AC 10 (R169)
def test_link_step_runs_as_normal_user_with_temp_home(skill_text: str, tmp_path: Path) -> None:
    lines = link_lines(skill_text)
    assert lines, "no `ln` command in a fenced shell block"
    assert not any(re.search(r"\bsudo\b", line) for line in lines)
    home = tmp_path / "home"
    home.mkdir()
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home)}
    result = subprocess.run(
        ["bash", "-c", "set -e\n" + "\n".join(lines)],
        env=env,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    link = home / ".local" / "bin" / "s1ft"
    assert link.is_symlink()
    assert os.readlink(link) == APP_HELPER
    # Running the step twice must still work.
    again = subprocess.run(
        ["bash", "-c", "set -e\n" + "\n".join(lines)],
        env=env,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert again.returncode == 0, again.stderr
    assert os.readlink(link) == APP_HELPER


def test_skill_does_not_ask_for_administrator_rights(skill_text: str) -> None:
    assert not re.search(r"\bsudo\b", skill_text)


# AC 11 (R84)
def online() -> bool:
    try:
        socket.create_connection(("github.com", 443), timeout=5).close()
    except OSError:
        return False
    return True


@pytest.mark.network
def test_npx_skills_add_installs_into_temp_home(tmp_path: Path) -> None:
    if shutil.which("npx") is None:
        pytest.skip("npx is not installed")
    if not online():
        pytest.skip("github.com is not reachable")
    home = tmp_path / "home"
    home.mkdir()
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "CI": "1",
        "DISABLE_TELEMETRY": "1",
    }
    result = subprocess.run(
        [
            "npx",
            "--yes",
            "skills",
            "add",
            "s1ft-app/skills",
            "--skill",
            "s1ft",
            "-a",
            "claude-code",
            "-y",
        ],
        env=env,
        cwd=home,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    installed = [p for p in home.rglob("SKILL.md") if p.parent.name == "s1ft"]
    assert installed, f"no s1ft/SKILL.md under the temp HOME\n{result.stdout}\n{result.stderr}"
    assert "name: s1ft" in installed[0].read_text(encoding="utf-8")
