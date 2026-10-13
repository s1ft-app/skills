# skills

Agent skills for s1ft meeting data (Claude Code, Codex, Cursor, Gemini CLI).

## Install

Two ways. Pick one.

**Any agent (Claude Code, Codex, Cursor, Gemini CLI)** with the `skills` CLI:

```bash
npx skills add s1ft-app/skills --skill s1ft
```

**Claude Code plugin.** This repo is also a plugin marketplace (`s1ft-skills`) with one plugin (`s1ft`) that holds all the skills:

```bash
claude plugin marketplace add s1ft-app/skills
claude plugin install s1ft@s1ft-skills
```

Inside a Claude Code session, use `/plugin marketplace add s1ft-app/skills` and `/plugin install s1ft@s1ft-skills`. Plugin skills are namespaced, for example `/s1ft:s1ft` and `/s1ft:decision-log`.

The `s1ft` skill reads your local meeting folders through the `s1ft` command line that ships inside S1ft.app. It sets up the link `~/.local/bin/s1ft` the first time it runs. Nothing leaves your Mac.

## Skills

| Skill | What it does |
|---|---|
| `s1ft` | Data access (`meetings list/search/show`, `voice stats`), the three data file formats, and how to read pauses, pace, uptalk, fillers and interruptions. |
| `follow-up-email` | Drafts a follow-up email. Only when the meeting had external attendees. |
| `decision-log` | Writes the decisions of a meeting as a log (reason, owner, time). |
| `action-items` | Lists the commitments with owner and due date. |
| `review-my-delivery` | Evidence-based look at your pauses, pace, uptalk, fillers and interruptions in one meeting. |
| `meeting-type` | Names the kind of meeting from the attendees, speakers, length and content. |
| `weekly-trends` | Compares your speaking numbers week by week. |

The library skills rely on the `s1ft` skill for data access. Each has an "Adapt this skill" section: copy the skill, then change those parts. Install one with `npx skills add s1ft-app/skills --skill <name>`.

## Skill format

Each skill is `skills/<name>/SKILL.md`. Rules, checked by `scripts/validate_skills.py`:

- Only Agent Skills standard top-level keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
- `name` equals the folder name.
- `metadata.s1ft-uses` is a comma separated string of `transcript`, `meeting`, `voice`.

## Plugin manifests

`.claude-plugin/marketplace.json` lists the one plugin, with `"source": "./"` (the repo root). `.claude-plugin/plugin.json` names it and sets the version. Claude Code finds the skills in `skills/<name>/SKILL.md` by default, so the skill folders stay where `npx skills add` expects them. The plugin cache copies the whole repo root, including `tests/` and `scripts/`. Keep the two version fields equal. `tests/test_plugin_manifest.py` checks the manifests, runs `claude plugin validate . --strict`, and installs from the local repo into a temporary config dir (both tests skip when `claude` is not on PATH).

## Contributing

Post an idea in [Discussions](https://github.com/s1ft-app/skills/discussions) first, then open a pull request. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the rules.

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_skills.py   # exit 0 valid, 1 invalid
.venv/bin/ruff check . && .venv/bin/mypy scripts tests && .venv/bin/python -m pytest
```
