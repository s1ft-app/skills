# Contributing

Thank you for adding a skill. Read this page before you open a pull request.

## 1. Post the idea first

Post an idea in [Discussions](https://github.com/s1ft-app/skills/discussions) (category "Ideas") before you open a pull request. Say what the skill does and which meeting data it reads. Open the pull request after the idea has a response.

## 2. Format rules

Each skill is `skills/<name>/SKILL.md`. `scripts/validate_skills.py` checks these rules:

- The frontmatter has only these top-level keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
- `name` equals the folder name.
- `description` is present and not empty.
- `metadata` holds the key `s1ft-uses`: a comma separated string of `transcript`, `meeting`, `voice`.

## 3. Commands

Set up once:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
```

Run before each pull request:

```bash
.venv/bin/python scripts/validate_skills.py
.venv/bin/ruff check .
.venv/bin/mypy scripts tests
.venv/bin/python -m pytest -m "not network"
```

The same four checks run in the job `checks` of the CI workflow. The workflow needs no secret and no `claude` command.

## 4. Shared skill rules

- Get data through the base skill `s1ft`. Do not read a file in the folder of another skill.
- Add an "Adapt this skill" section: say which parts a user may change after a copy.
- For an empty result, use the rule of the base skill.
- When you quote the user, give the `start` time of the segment.
- For a period, read one meeting at a time and keep only the results.
- Put no personal path and no email address in a skill.
- A test must never write a file in the real `~/Library/Application Support/s1ft/`.
- Do not state a number of skills in a description.

Text rules for a delivery skill:

- Describe the data. Do not judge the user.
- Give no score, no grade and no label about the person.
- Do not state an ideal number as a rule.
- Do not comment on the delivery of another speaker.

## 5. Review of a delivery skill

A delivery skill is a skill that reads how a person speaks (pauses, pace, uptalk, fillers, interruptions). The `communication-coach` agent must review its text before the pull request merges. Put the result of the review in a review comment on the pull request. Fix each result, or give the reason not to fix it in the comment.

## 6. Merge and release

- The owner decides which pull request merges.
- Each change, also from the owner, comes through a pull request. Nobody pushes to `main`.
- The owner merges only after the required checks pass.
- A merged skill ships in the plugin `s1ft`.

## License

By contributing you agree that your work is under the Apache License 2.0 (see `LICENSE`).
