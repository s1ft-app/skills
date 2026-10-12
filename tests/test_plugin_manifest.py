"""Claude Code plugin marketplace manifests: .claude-plugin/marketplace.json and plugin.json."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO

MANIFEST_DIR = REPO / ".claude-plugin"
MARKETPLACE = MANIFEST_DIR / "marketplace.json"
PLUGIN = MANIFEST_DIR / "plugin.json"
SKILLS = REPO / "skills"
RESERVED_PLUGIN_PREFIXES = ("claude-", "anthropic-", "cc-plugin-")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EXPECTED_SKILLS = {
    "s1ft",
    "action-items",
    "decision-log",
    "follow-up-email",
    "meeting-type",
    "review-my-delivery",
    "weekly-trends",
}
HAS_CLAUDE = shutil.which("claude") is not None


def load(path: Path) -> dict[str, Any]:
    assert path.is_file(), f"{path.relative_to(REPO)} does not exist"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_manifests_parse() -> None:
    load(MARKETPLACE)
    load(PLUGIN)


def test_marketplace_required_fields() -> None:
    data = load(MARKETPLACE)
    assert data["name"] == "s1ft-skills"
    assert NAME_RE.match(data["name"])
    assert isinstance(data["owner"], dict)
    assert data["owner"]["name"] == "s1ft-app"
    assert isinstance(data.get("description"), str) and data["description"].strip()
    assert isinstance(data["plugins"], list) and data["plugins"]


def test_marketplace_plugin_entries() -> None:
    entries = load(MARKETPLACE)["plugins"]
    assert [entry["name"] for entry in entries] == ["s1ft"]
    for entry in entries:
        assert NAME_RE.match(entry["name"])
        assert not entry["name"].startswith(RESERVED_PLUGIN_PREFIXES)
        source = entry["source"]
        assert isinstance(source, str) and source.startswith("./")
        assert (REPO / source).is_dir()


def test_plugin_json_fields() -> None:
    data = load(PLUGIN)
    assert data["name"] == "s1ft"
    assert not data["name"].startswith(RESERVED_PLUGIN_PREFIXES)
    assert isinstance(data.get("description"), str) and data["description"].strip()
    assert data["author"] == {"name": "s1ft-app"}
    assert re.match(r"^\d+\.\d+\.\d+$", data["version"])
    assert "skills" not in data, "omit `skills`: default scan of skills/<name>/SKILL.md"


def test_names_and_versions_consistent() -> None:
    plugin = load(PLUGIN)
    for entry in load(MARKETPLACE)["plugins"]:
        assert entry["name"] == plugin["name"]
        if "version" in entry:
            assert entry["version"] == plugin["version"]


def test_all_seven_skills_discoverable() -> None:
    folders = {p.name for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith(".")}
    assert folders == EXPECTED_SKILLS
    for name in folders:
        assert (SKILLS / name / "SKILL.md").is_file()


def test_no_personal_paths_or_emails() -> None:
    for path in (MARKETPLACE, PLUGIN):
        text = path.read_text(encoding="utf-8")
        assert "/Users/" not in text and "/home/" not in text
        assert "@" not in text, f"possible email in {path.name}"


@pytest.mark.skipif(not HAS_CLAUDE, reason="claude CLI is not installed")
def test_claude_plugin_validate_strict(tmp_path: Path) -> None:
    result = subprocess.run(
        ["claude", "plugin", "validate", str(REPO), "--strict"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=isolated_env(tmp_path),
    )
    assert result.returncode == 0, result.stdout + result.stderr


def isolated_env(tmp_path: Path) -> dict[str, str]:
    home = tmp_path / "home"
    config = tmp_path / "cfg"
    home.mkdir(exist_ok=True)
    config.mkdir(exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["CLAUDE_CONFIG_DIR"] = str(config)
    return env


@pytest.mark.skipif(not HAS_CLAUDE, reason="claude CLI is not installed")
def test_install_from_local_repo_end_to_end(tmp_path: Path) -> None:
    env = isolated_env(tmp_path)
    config = Path(env["CLAUDE_CONFIG_DIR"])
    assert config.is_relative_to(tmp_path) and Path(env["HOME"]).is_relative_to(tmp_path)

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["claude", "plugin", *args],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            env=env,
            cwd=tmp_path,
        )

    added = run("marketplace", "add", str(REPO))
    assert added.returncode == 0, added.stdout + added.stderr
    installed = run("install", "s1ft@s1ft-skills")
    assert installed.returncode == 0, installed.stdout + installed.stderr

    cache = config / "plugins" / "cache" / "s1ft-skills" / "s1ft"
    versions = [p for p in cache.iterdir() if p.is_dir()]
    assert len(versions) == 1
    installed_skills = {
        p.name for p in (versions[0] / "skills").iterdir() if (p / "SKILL.md").is_file()
    }
    assert installed_skills == EXPECTED_SKILLS
    assert "s1ft" in installed_skills
