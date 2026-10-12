---
name: follow-up-email
description: Use when the user wants a follow-up email after a meeting with people outside their own company, for example a client or a partner. Drafts the email from the transcript. Does nothing when the meeting had no external attendees.
compatibility: Needs the s1ft skill and the s1ft macOS app (S1ft.app) with at least one recorded meeting.
allowed-tools: Bash(s1ft:*) Read
metadata:
  s1ft-uses: "transcript,meeting"
---

# Follow-up email

Draft a short follow-up email for one meeting. The skill only makes sense when someone outside the user's organisation was in the meeting. It writes a draft. It never sends anything.

## 1. Get the data

Use the `s1ft` skill for data access. Do not repeat its setup here.

1. Pick the meeting. If the user gave no meeting, take the newest one: `s1ft meetings list --json`. Take the first row.
2. Run `s1ft meetings show <id> --json`. You need `meeting.calendarEvents[].attendees` and `transcript.segments`.
3. If `s1ft` cannot run, read `meeting.json` and `transcript.json` directly from the meeting folder, as the `s1ft` skill describes.

## 2. Check for external attendees. Stop if there are none.

An attendee is external when the email domain differs from the user's own domain.

1. Use the attendees of the event with `usedForName: true`. If no event has it, use the event that overlaps the meeting time most. If there is no event, there are no attendees.
2. Find the user's own domain: ask the user once, or use the domain in "Adapt this skill". Do not guess it from the data.
3. Ignore attendees without an email. Ignore resource calendars (rooms).
4. If no attendee is external, stop. Tell the user: "No external attendees in this meeting, so I wrote no follow-up." Do not write a draft.

## 3. Write the draft

- To: the external attendees (name and email from the calendar event). The user adds Cc.
- Subject: `Follow-up: <meeting name>`.
- Body, in the language of the meeting, in this order:
  1. One line of thanks.
  2. What was agreed, as a short list. Only things the transcript states.
  3. Next steps: who does what, and by when if someone said a date. Use names from the calendar attendees when the transcript only says `Participant`.
  4. One closing line.
- Keep it under 150 words. No new promises, prices or dates that the transcript does not contain.
- If you are not sure who owns a step or when it is due, write "to confirm" and tell the user.

Show the draft in the chat. Do not send it and do not create it in a mail app unless the user asks.

## Adapt this skill

Change these parts to fit you:

- **Your own domain(s).** Replace the question in step 2 with your domains, for example `example.com, example.org`.
- **Who counts as external.** Add domains you treat as internal (a parent company, a contractor).
- **Tone and length.** Formal or friendly, a different word limit, a signature block.
- **Language.** Fix one language instead of the meeting language.
- **Structure.** Add sections such as "Open questions" or "Attachments to send".
