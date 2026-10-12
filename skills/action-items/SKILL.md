---
name: action-items
description: Use when the user wants the tasks, commitments and next steps from a meeting, with an owner and a due date when someone said them. Reads the transcript.
compatibility: Needs the s1ft skill and the s1ft macOS app (S1ft.app) with at least one recorded meeting.
allowed-tools: Bash(s1ft:*) Read
metadata:
  s1ft-uses: "transcript,meeting"
---

# Action items

List what people committed to do in a meeting.

## 1. Get the data

Use the `s1ft` skill for data access. Do not repeat its setup here.

- Run `s1ft meetings show <id> --json`. If the user gave no meeting, take the newest from `s1ft meetings list --json`.
- You need `transcript.segments` and, for names, `meeting.calendarEvents[].attendees`.
- If `s1ft` cannot run, read `meeting.json` and `transcript.json` directly from the meeting folder.

## 2. Find the action items

An action item is a commitment to do something after the meeting.

- Look for: "I will...", "I'll send...", "can you...?" followed by a yes, "let's follow up on...", "by Friday", "next week".
- Skip ideas that nobody took up, and things that were done during the meeting.
- Owner: the speaker who took it. `Me` is the user. For other people, use the calendar attendee name if the transcript or the calendar makes it clear. Otherwise write the speaker label (`Participant 2`) and mark it "owner to confirm".
- Due date: only when a speaker said one. Turn "Friday" into a date from `meeting.start`. If it is unclear, copy the words as said.
- Do not invent items to fill a list. An empty list is a valid result.

## 3. Write the list

One line per item: `[ ] <owner>: <what> (due <date or "not stated">) [mm:ss]`. The time is the segment `start`.

Put the user's own items (`Me`) first, then the others. Finish with the items that need confirmation.

## Adapt this skill

Change these parts to fit you:

- **Only your own items**, or everybody's.
- **Item format.** A checklist, a table, or the format of your task tool (a Markdown file, a ticket text).
- **Due date rules.** A default due date when none was said, or a week start other than Monday.
- **Names.** A map from speaker labels to people you know.
- **Where it goes.** A file the agent appends to, for example a project task file.
