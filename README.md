# skills

Agent skills for s1ft meeting data (Claude Code, Codex, Cursor, Gemini CLI).

## Install

```bash
npx skills add s1ft-app/skills --skill s1ft
```

The `s1ft` skill reads your local meeting folders through the `s1ft` command line that ships inside S1ft.app. It sets up the link `~/.local/bin/s1ft` the first time it runs. Nothing leaves your Mac.

## Skills

| Skill | What it does |
|---|---|
| `s1ft` | Data access (`meetings list/search/show`, `voice stats`), the three data file formats, and how to read pauses, pace, uptalk, fillers and interruptions. |

## Skill format

Each skill is `skills/<name>/SKILL.md`. Rules, checked by `scripts/validate_skills.py`:

- Only Agent Skills standard top-level keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
- `name` equals the folder name.
- `metadata.s1ft-uses` is a comma separated string of `transcript`, `meeting`, `voice`.

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_skills.py   # exit 0 valid, 1 invalid
.venv/bin/ruff check . && .venv/bin/mypy scripts tests && .venv/bin/python -m pytest
```
