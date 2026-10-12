---
name: decision-log
description: Use when the user wants the decisions of a meeting, or of several meetings, written down as a log with the reason, the owner and the time in the recording. Reads the transcript.
compatibility: Needs the s1ft skill and the s1ft macOS app (S1ft.app) with at least one recorded meeting.
allowed-tools: Bash(s1ft:*) Read
metadata:
  s1ft-uses: "transcript,meeting"
---

# Decision log

Find the decisions in a meeting and write them as a log the user can keep.

## 1. Get the data

Use the `s1ft` skill for data access. Do not repeat its setup here.

- One meeting: `s1ft meetings show <id> --json`. Use `meeting.name`, `meeting.start` and `transcript.segments`.
- Several meetings: `s1ft meetings list --since <date> --until <date> --json`, or `s1ft meetings search <text>`, then `show` for each.
- If `s1ft` cannot run, read `meeting.json` and `transcript.json` directly from the meeting folders.

## 2. Find the decisions

A decision is a statement that a choice was made. It is not a topic, an opinion or an idea.

- Count it when someone states the choice and nobody objects: "we will...", "let's go with...", "agreed", "decided", "OK, so we do X".
- Do not count a proposal that was not accepted, or one that was postponed. List those in "Open" instead.
- If the speakers disagree, or the transcript is unclear, say so. Do not make a decision up.

## 3. Write the log

One entry per decision, in the order they happened:

- **Decision**: one sentence.
- **Why**: the reason, only if someone said it.
- **Owner**: who carries it out, only if someone said it. Otherwise "not stated".
- **When**: the segment `start` as `mm:ss`, and the date of the meeting.
- **Quote**: the exact `text` of the segment, short.

After the entries, add a short "Open" list for items that were discussed and not decided.

For several meetings, group by meeting, newest first. If the same topic is decided again, mark the earlier entry as changed.

## Adapt this skill

Change these parts to fit you:

- **Which meetings.** Run it only for some meetings, for example client calls: filter by name or by the attendee domains in `calendarEvents`.
- **Entry fields.** Add "Impact" or "Risk"; remove "Quote".
- **Where the log goes.** A file path, for example a markdown file per project that the agent appends to.
- **Decision words.** Add the phrases your team uses, in your language.
- **Output format.** A table, a list, or a format your wiki accepts.
