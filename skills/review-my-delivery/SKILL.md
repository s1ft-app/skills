---
name: review-my-delivery
description: Use when the user wants feedback on how they spoke in a meeting: pauses, pace, uptalk, filler words and interruptions. Describes what the voice and transcript data show, with evidence, and suggests one thing to try.
compatibility: Needs the s1ft skill and the s1ft macOS app (S1ft.app) with a recorded meeting that has voice data.
allowed-tools: Bash(s1ft:*) Read
metadata:
  s1ft-uses: "transcript,meeting,voice"
---

# Review my delivery

Give the user an honest, evidence-based look at how they spoke in one meeting. The voice data covers only the user (`Me`). It is a sensor reading, not a verdict.

## 1. Get the data

Use the `s1ft` skill for data access and for the rules that read pauses, pace, uptalk, fillers and interruptions. Do not repeat them here.

1. Pick the meeting. Without one from the user, take the newest: `s1ft meetings list --json`.
2. `s1ft meetings show <id> --json` for the transcript and the meeting.
3. `s1ft voice stats <id> --json` for the voice numbers. Use the defaults: silence threshold -50 dBFS, minimum silence 300 ms, percentiles p10, p50 and p90. Change them only if the user asks.
4. If `s1ft` cannot run, read `meeting.json`, `transcript.json` and `telemetry.json` directly from the meeting folder and compute the numbers by the rules in the `s1ft` skill.
5. If there is no voice data (exit code 3, or an old `telemetry.json`), say so and review the transcript only: fillers, pace and interruptions.

## 2. Check that there is enough data

- Less than about 2 minutes of the user's speech, or fewer than 5 `Me` segments: say the sample is too small for patterns. Give the numbers and stop.
- A meeting where the user mostly listened: say that, and keep the review short.
- Check the kind of meeting first (use `meeting-type`, or ask). Standups: give the numbers only, with no tip. One-on-one and small groups: do not suggest more talk time or a slower pace as a default. Presentations: pace and pauses matter most, and interruptions rarely apply. Do not give "ask more questions" advice for a presentation, or "rehearse your opening" advice for a one-on-one.

## 3. Measure

For the user's speech, report these with the numbers behind them:

- **Pauses.** Silences per minute and the share of time in silence (`silenceCount`, `silenceTotalSec`). Separate pauses inside a turn from the gap before the user answers.
- **Pace.** Words per minute: the median and the range over segments of 10 seconds or more.
- **Uptalk.** Statements that end on a rising pitch, as a count and a share of statements. Skip questions.
- **Fillers.** Count and rate per minute of the user's speech, by word.
- **Interruptions.** How often the user started speaking over someone, and how often someone did so over the user.

Quote at most three short examples with the segment `start` time.

## 4. Write the review

Keep it short and in this order:

1. **What stood out.** The one or two measures that differ most from the user's own usual range or from the other measures in this meeting. Say "in this meeting".
2. **What went well.** At least one thing the data supports, for example steady pace or few fillers.
3. **One thing to try.** One concrete action for the next meeting, tied to a number and suited to the kind of meeting. For example: "Your answers started after 0.4 s on average. If it feels natural, try a short pause before you answer."
4. **Limits.** What the data cannot tell: the setting, the topic, the audience, whether a rising pitch was a question, a habit or a deliberate invitation, how other people spoke.

Rules for tone and claims:

- Describe, do not judge. Write "you used 9 fillers in 12 minutes", not "you used too many fillers".
- No scores, grades or labels about the person (nervous, confident, weak).
- No ideal numbers presented as a rule. Pace and pauses suit the situation. If you compare, name the source and say it is a rough guide. Do not use a words-per-minute range or a filler percentage as a pass mark.
- Fillers and pauses are normal speech. Do not present "fewer" as the goal. Very few fillers is not better, and a pause before a key point is a tool.
- Do not claim a cause. A fast pace can be excitement, a short slot or a habit.
- One meeting is one sample. Do not call it a pattern. Point to `weekly-trends` for patterns.
- Do not comment on the other speakers' delivery. There is no voice data for them.

## Adapt this skill

Change these parts to fit you:

- **Focus.** Keep only the measures you work on, for example only fillers and pace.
- **Filler words.** Your list, in your language, including words that are not fillers for you.
- **Thresholds.** The values for `--silence-threshold-dbfs`, `--min-silence-ms` and `--percentiles`, if the defaults do not suit your microphone or room.
- **Meeting kinds.** Review only some meetings, for example presentations or client calls.
- **Tone and length.** Shorter, or more detailed; add a target you chose yourself.
- **Output.** A file where the agent saves each review.
