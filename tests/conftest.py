from __future__ import annotations

import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
VALIDATOR = REPO / "scripts" / "validate_skills.py"
BASE_SKILL = REPO / "skills" / "s1ft" / "SKILL.md"
SKILLS_DIR = REPO / "skills"
FIXTURES = REPO / "tests" / "fixtures"
REAL_SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "s1ft"

# New skills follow the shared skill rules (skills-library R1 to R27). A later skill feature adds
# its name here. DELIVERY_SKILLS holds the new skills that describe how the user speaks
# (R17 to R20).
NEW_SKILLS: list[str] = ["summary"]
DELIVERY_SKILLS: list[str] = []


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


def list_files(root: Path) -> list[str]:
    """Sorted relative paths of all files under root. Empty when root does not exist."""
    if not root.is_dir():
        return []
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())


@pytest.fixture(scope="session", autouse=True)
def real_support_dir_untouched() -> Iterator[None]:
    """R27: no test writes a file in the real ~/Library/Application Support/s1ft/.

    Lists the files before and after the run. Only reads the folder.
    """
    before = list_files(REAL_SUPPORT_DIR)
    yield
    after = list_files(REAL_SUPPORT_DIR)
    assert before == after, (
        "a test changed the real Application Support/s1ft folder: "
        f"added {sorted(set(after) - set(before))}, removed {sorted(set(before) - set(after))}"
    )


@pytest.fixture
def skills_dir(tmp_path: Path) -> Path:
    path = tmp_path / "skills"
    path.mkdir()
    return path
