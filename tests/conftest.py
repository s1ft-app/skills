from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
VALIDATOR = REPO / "scripts" / "validate_skills.py"
BASE_SKILL = REPO / "skills" / "s1ft" / "SKILL.md"


def write_skill(
    skills_dir: Path,
    folder: str,
    frontmatter: str,
    body: str = "# Skill\n\nDo the work.\n",
) -> Path:
    path = skills_dir / folder
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(f"---\n{frontmatter.strip()}\n---\n\n{body}", encoding="utf-8")
    return path


def good_frontmatter(name: str = "demo", uses: str = "transcript, meeting") -> str:
    return (
        f"name: {name}\n"
        "description: Use when the user asks about a demo meeting.\n"
        "metadata:\n"
        f'  s1ft-uses: "{uses}"\n'
    )


def run_validator(skills_dir: Path) -> subprocess.CompletedProcess[str]:
    """Run the validator as a subprocess. Exit 0 = valid, 1 = invalid skill found.

    A missing script makes Python exit 2, so a missing validator never counts as a
    correct rejection.
    """
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(skills_dir)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


@pytest.fixture
def skills_dir(tmp_path: Path) -> Path:
    path = tmp_path / "skills"
    path.mkdir()
    return path
