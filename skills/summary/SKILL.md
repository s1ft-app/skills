---
name: summary
description: Use when the user asks for a summary of a meeting, the bottom line, the key decisions, open issues or action items of a call. Reads the transcript and the meeting details and gives the summary in the reply.
compatibility: Needs the s1ft skill and the s1ft macOS app (S1ft.app) with at least one recorded meeting.
allowed-tools: Bash(s1ft:*) Read
metadata:
  s1ft-uses: "transcript,meeting"
---

# Summary

Write a short summary of one meeting. The text below is the same text the "Summary" prompt in S1ft.app uses. Follow it, using the data from this section.

## 1. Get the meeting data

Use the `s1ft` skill for data access. Do not repeat its setup here.

- Find the meeting: `s1ft meetings list --json`, or `s1ft meetings search <text> --json`. If the user names no meeting, take the newest one and say which one you took.
- Read it: `s1ft meetings show <id> --json`. The "meeting" part holds `meeting.name`, `meeting.start` and `calendarEvents` (titles and attendees). The "transcript" part holds `transcript.segments`.
- If `s1ft` cannot run, read `meeting.json` and `transcript.json` directly from the meeting folder.
- If a list or search result is empty, follow the rule of the `s1ft` skill for an empty result. Do not guess a folder.
- Use the calendar event title as the title only when `meeting.json` has a calendar event with a title. Otherwise use `meeting.name`.
- The attendees are the `attendees` of `calendarEvents`. Speaker labels in `transcript.segments` (`Me`, `Participant`) are not names.

Give the summary in the reply. Do not write it to a file, and do not create or change `summary.md` or any other file in the meeting folder.

When you quote a segment, use its `text` as it is and give the `start` time of the segment as `mm:ss`.

## The summary prompt

You are a meeting-notes assistant. Given a raw transcript, produce a concise summary in Markdown. Keep the ENTIRE summary under 500 words. Use the meeting title as the top-level heading.

Include these sections:

## Bottom Line
2-3 sentences: what was this meeting about and what is the single most important outcome? Write this so someone who skips everything else still gets the point.

## Decisions & Key Facts
- Bullet only things that were DECIDED, AGREED, or CONFIRMED — not things merely discussed.
- Include specific numbers, dates, and commitments (dollar amounts, headcount, deadlines).
- 3-7 bullets max. If nothing was decided, write "No formal decisions."

## Open Issues
- Bullet unresolved questions, risks, or blockers that still need answers.
- Skip this section if everything was resolved.

## Action Items
- Bullet concrete next steps. Each item should be a clear, actionable task.
- Name an owner only when the transcript says explicitly who will do it AND that person is a listed attendee. Never infer an owner from speaker labels — they are unreliable.

Writing rules:
- Be specific over comprehensive. One concrete detail beats three vague ones.
- Omit pleasantries, status updates with no new information, and any topic that produced no decision, question, or action.
- Never pad with filler. If a meeting was short or simple, the summary should be short.
- Omit any section that has no content.

Meeting data: when the `meeting` data has a calendar event title, use that title for the top-level heading.

## Adapt this skill

Copy this skill, then change these parts to fit you:

- **The prompt.** Change the sections, the word limit or the writing rules in the text above.
- **Language.** Ask for the summary in your own language.
- **Which meetings.** Run it only for some meetings, for example client calls: filter by name or by the attendee domains in `calendarEvents`.
- **Where the summary goes.** Add a file path or a tool, if you want the agent to save it.
- **Output format.** A list, a table, or a format your wiki accepts.

This skill is a copy of the built-in prompt. A change to this skill does not change the "Summary" in the S1ft app. A change in the app does not change this skill. You may need to copy the new text again.
