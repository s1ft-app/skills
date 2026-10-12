---
name: weekly-trends
description: Use when the user wants to see how their speaking changes over weeks: pauses, pace, uptalk, fillers and interruptions across many meetings. Compares weeks with the numbers and says when the data is too thin.
compatibility: Needs the s1ft skill and the s1ft macOS app (S1ft.app) with recorded meetings that have voice data.
allowed-tools: Bash(s1ft:*) Read
metadata:
  s1ft-uses: "transcript,meeting,voice"
---

# Weekly trends

Show how the user's speaking changed from week to week. s1ft stores raw facts for each meeting. This skill adds the comparison over time.

## 1. Get the data

Use the `s1ft` skill for data access and for the rules that read pauses, pace, uptalk, fillers and interruptions. Do not repeat them here.

1. Choose the period. Default: the last 4 full weeks (Monday to Sunday, local time) and the current week so far. `s1ft meetings list --since <date> --until <date> --json`.
2. For each meeting: `s1ft meetings show <id> --json` and `s1ft voice stats <id> --json`. Use the defaults: silence threshold -50 dBFS, minimum silence 300 ms, percentiles p10, p50 and p90. Use the same options for every meeting, or the weeks are not comparable.
3. If `s1ft` cannot run, read the data files of each meeting folder directly and compute the numbers by the rules in the `s1ft` skill.
4. Skip a meeting without voice data (exit code 3, or an old `telemetry.json`) for the voice measures, and say how many you skipped.

## 2. Compute per week

For each week, from the user's speech (`Me`) only:

- Meetings counted, and minutes of the user's speech.
- Silences per minute and the share of time in silence.
- Words per minute: the median.
- Share of statements with rising pitch at the end (uptalk).
- Fillers per minute.
- Interruptions the user made, and interruptions the user received, per hour of meeting.

Weight by speaking time: add counts and minutes over the week, then divide. Do not average the averages of meetings.

## 3. Check that there is enough data

- A week with fewer than 3 meetings or fewer than about 10 minutes of the user's speech is "thin". Show its numbers, mark them thin, and do not draw a trend from it.
- Fewer than 3 usable weeks: say there is not enough data for a trend yet and show the weeks you have.
- Different kinds of meeting change the numbers. A week of presentations differs from a week of standups. Use `meeting-type` if the user wants this split out. Compare weeks of the same kind of meeting where you can.
- Standups are not coaching targets. Count them for volume only, and suggest no changes from them.

## 4. Write the report

1. **A table**: one row per week, one column per measure, thin weeks marked.
2. **Changes.** Name only changes that are clear: the same direction over at least 3 weeks, or a change much larger than the week-to-week variation. Three weeks in one direction can be chance: say "has moved in one direction for three weeks", not "is improving", unless the change is also larger than the usual week-to-week range. Write "fillers per minute went from 1.8 to 1.1 over four weeks". For other measures write "no clear change".
3. **Possible reasons**, as questions to the user, not as facts: "Did you present more this week?"
4. **One thing to keep or try**, tied to a number. Prefer "keep" when a measure is in a steady range. Do not suggest chasing a lower or higher number for its own sake.
5. **Limits.** Small samples, different meeting kinds, one microphone, and that the numbers do not say how the speech was received.

Rules for tone and claims:

- Describe, do not judge. No scores, grades or labels about the person.
- No ideal numbers presented as a rule.
- Do not say the user "improved" or "got worse" for a change inside the normal week-to-week variation. Say "changed" or "stayed about the same".
- Show the numbers behind every statement. Show raw counts next to rates, because small counts swing widely.
- When a change is clear and in the direction the user is working on, say it plainly and warmly, for example "Your fillers per minute went from 1.8 to 1.1 over four weeks. That is a real change." Do not hide good news behind caveats.
- Correlation is not cause. Do not claim that something the user did caused a change.

## Adapt this skill

Change these parts to fit you:

- **Period.** More or fewer weeks, months instead of weeks, a different week start.
- **Measures.** Keep only the ones you work on.
- **Which meetings.** Count only some, for example meetings with external attendees or meetings over 20 minutes.
- **Filler words.** Your list, in your language.
- **Thresholds.** The silence options and the percentiles, if the defaults do not suit you. Keep them the same for every week.
- **Run it on a schedule.** For example a weekly scheduled task that saves the report to a file.
