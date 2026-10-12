---
name: meeting-type
description: Use when the user wants to know what kind of meeting a recording was (one-on-one, standup, client call, interview, workshop and so on), or wants meetings sorted by type. Reads the meeting data and the transcript.
compatibility: Needs the s1ft skill and the s1ft macOS app (S1ft.app) with at least one recorded meeting.
allowed-tools: Bash(s1ft:*) Read
metadata:
  s1ft-uses: "transcript,meeting"
---

# Meeting type

s1ft does not label meetings. This skill reads the signals and gives a type, with the evidence.

## 1. Get the data

Use the `s1ft` skill for data access. Do not repeat its setup here.

- One meeting: `s1ft meetings show <id> --json`.
- Many meetings: `s1ft meetings list --since <date> --json`, then `show` for each.
- If `s1ft` cannot run, read `meeting.json` and `transcript.json` directly from the meeting folders.

## 2. Collect the signals

- **Attendees.** The number of people in `calendarEvents[].attendees`. The email domains: one domain is internal, more than one means external people. A meeting without a calendar event has no attendee data.
- **Speakers.** The distinct `speaker` values in the transcript, and each one's share of the talking time (sum of `end` minus `start`).
- **Length.** `meeting.end` minus `meeting.start`.
- **Title.** The words in `meeting.name`, such as "1:1", "standup", "sync", "interview", "demo", "review".
- **Content.** Who asks questions, who talks most, whether people go round one by one, whether someone presents.

## 3. Choose a type

| Type | Typical signals |
|---|---|
| one-on-one | 2 people, 15 to 60 min, personal or status talk, both speak a lot |
| standup | 3 or more people, under 20 min, each says what is done, next, blocked |
| team meeting | 3 or more people, one domain, discussion and decisions |
| client call | an external domain, requirements, price, schedule, status |
| interview | 2 or more people, one asks most of the questions, the other talks most |
| presentation or webinar | one speaker above 70% of the time, few questions |
| workshop or brainstorm | many people, long, many short turns, ideas and notes |
| other | none of the above fits |

Give: the type, a confidence (high, medium or low), and the two or three signals behind it. When two types fit, name both. When the data is thin (no calendar event, a very short transcript), say so and lower the confidence. Do not claim a type the signals do not support.

For many meetings, give one line per meeting (`date, name, type, confidence`) and a count per type.

## Adapt this skill

Change these parts to fit you:

- **The types.** Add your own (for example "sales demo", "retro") or remove ones you never have.
- **The signals.** Rules that fit your work, such as a title prefix or a particular attendee.
- **Own domain(s).** Tell the skill which email domains are internal.
- **Output.** A single word, a table, or a tag line that you paste into your notes.
