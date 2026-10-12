---
name: s1ft
description: Use when the user asks about their recorded meetings, what was said in a call, a transcript, a meeting summary, or how they spoke (pauses, pace, uptalk, fillers, interruptions). Reads the local s1ft meeting folders through the s1ft command line.
compatibility: Needs the s1ft macOS app (S1ft.app) with at least one recorded meeting.
allowed-tools: Bash(s1ft:*) Read
metadata:
  s1ft-uses: "transcript,meeting,voice"
---

# s1ft meetings

s1ft records meetings on the user's Mac and keeps every meeting in its own folder. This skill reads that data. It never changes it. Everything stays on the device.

## 1. Set up the command line (once)

The app ships the command line inside `S1ft.app`. Link it into the user's own bin folder. Run this as the normal user. It is safe to run again.

```bash
mkdir -p ~/.local/bin
ln -sf /Applications/S1ft.app/Contents/Helpers/s1ft ~/.local/bin/s1ft
```

If `~/.local/bin` is not on the `PATH`, call `~/.local/bin/s1ft` by its full path.

## 2. Check the version, then stop if it is incompatible

Run `s1ft --version`. It prints `s1ft <version>`, for example `s1ft 1.3.0`. The command line ships with the app, so this is the app version.

- A version from 1.3.0 upward writes the files in this document.
- Each data file also carries a `schemaVersion`. This skill knows `meeting.json` 1, `transcript.json` 1 and `telemetry.json` 2.
- If the version is lower, or a file has another `schemaVersion`, treat it as incompatible. Stop and tell the user to update S1ft. Do not guess at the format.

## 3. The commands

All commands are read-only. Add `--json` to get JSON on stdout. Add `--dir <path>` to read another meetings folder. The default is the output folder set in the s1ft app (`~/Documents/s1ft Meetings` if the user never changed it).

| Command | What it does |
|---|---|
| `s1ft meetings list [--since D] [--until D]` | One meeting per line, newest first: `id`, tab, `start`, tab, `name`. |
| `s1ft meetings search <text> [--since D] [--until D]` | The same, only for meetings whose name or transcript text contains `<text>`. Case and accents are ignored. |
| `s1ft meetings show <id>` | Meeting details and the transcript. |
| `s1ft voice stats <id>` | Numbers per span from `telemetry.json`. Options: `--silence-threshold-dbfs` (default -50), `--min-silence-ms` (default 300), `--percentiles` (default 10,50,90). |
| `s1ft --version` | `s1ft <version>`. |

Details:

- `<id>` is the `id` UUID from `meeting.json` (first column of `meetings list`), in any letter case. It is not the folder name.
- `--since` and `--until` take `YYYY-MM-DD` (the whole local day, inclusive) or a full ISO 8601 instant such as `2026-10-12T09:30:00Z`.
- `meetings list --json` and `meetings search --json` print `{"meetings":[...]}`. Each row has `id`, `name`, `platform`, `start`, `end` and `directory` (the meeting folder).
- `meetings show <id> --json` prints `{"meeting": ..., "transcript": ..., "files": {"meeting": ..., "transcript": ..., "telemetry": ...}}`. `meeting` and `transcript` hold the parsed file contents. `files` holds the file paths. A file that does not exist is `null`. There is no voice block: use `s1ft voice stats`.
- `voice stats --json` prints `frameMs`, `options` and `spans`. Each span has `start`, `durationSec`, `frameCount`, `voicedFrameCount`, `pitchMinHz`, `pitchMaxHz`, `pitchRangeHz`, `pitchPercentilesHz` (keys such as `p10`, `p50`, `p90`), `rmsMeanDbfs`, `peakMaxDbfs`, `silenceCount` and `silenceTotalSec`.
- The command line never reads `transcript.md` (an old format). A meeting with only `transcript.md` shows `"transcript": null`.

Exit codes: `0` ok, `3` missing data (unknown id, missing meetings folder, no version 2 `telemetry.json`), `4` usage error (bad option or date). The message is on stderr and stdout is empty.

## 4. The meeting folder and its data files

A meeting folder holds `meeting.json`, usually `transcript.json`, and for newer meetings `telemetry.json`. A folder without `meeting.json` is not a meeting. Every file has a `schemaVersion`.

### `meeting.json` (schemaVersion 1)

- `schemaVersion`: 1
- `id`: the meeting UUID
- `name`: the meeting name (from the calendar, or set by the user)
- `platform`: the bundle id of the app that was recorded, or `manual`
- `start`, `end`: ISO 8601 instants, for example `2026-10-12T09:30:00Z`
- `calendarEvents`: calendar events that matched the time. Each one has:
  - `title`
  - `start`, `end`: ISO 8601
  - `isAllDay`: boolean
  - `attendees`: list of objects with `name` and `email` (either can be missing or null)
  - `usedForName`: true only when this event gave the meeting its name

### `transcript.json` (schemaVersion 1)

- `schemaVersion`: 1
- `segments`: list in time order. Each segment has:
  - `speaker`: `Me` for the user's microphone. Other people are `Participant`, or `Participant 1`, `Participant 2` and so on when the app told them apart.
  - `start`, `end`: seconds from the start of the recording (numbers)
  - `text`

### `telemetry.json` (schemaVersion 2)

Raw frames of the user's microphone only. It has no data about other speakers and no scores.

- `schemaVersion`: 2
- `source`: `microphone`
- `method`: how the frames were measured: `frameMs` (frame length), `windowSamples`, `pitchAlgorithm` and `pitchRangeHz` (min and max)
- `sampleRateHz`: sample rate of the audio
- `spans`: one span per "Me" segment. Each span has:
  - `start`: seconds from the start of the recording. Frame `i` starts at `start + i * frameMs / 1000`.
  - `pitchHz`: one value per frame, `null` where no pitch was found
  - `rmsDbfs`: one level per frame in dBFS
  - `peakDbfs`: one peak per frame in dBFS

An older meeting can hold a `telemetry.json` with `schemaVersion` 1 (summary numbers per utterance). It is incompatible with this skill: say so, and use the transcript only.

## 5. If the command line cannot run

If `s1ft` is not installed, or cannot run (the app is missing, or the call fails for a reason other than exit 3 or 4), read the data files directly. Find the meetings folder (default `~/Documents/s1ft Meetings`, or the folder the user names). Each subfolder with a `meeting.json` is one meeting. Read `meeting.json`, `transcript.json` and `telemetry.json` with the Read tool, and compute the numbers from the frames by the rules below. Check the `schemaVersion` of every file first.

## 6. How to read the voice data

Say what the data shows. Do not score the user and do not judge. Say when the data is not enough. Voice data covers only the user (`Me`).

- **Pauses.** Silence inside a span: `silenceCount` and `silenceTotalSec` from `s1ft voice stats`. Tune what counts as silence with `--silence-threshold-dbfs` and `--min-silence-ms`. Gaps between segments in `transcript.json` (next `start` minus this `end`) show pauses between turns. A pause before an answer is thinking time, not always a problem.
- **Pace.** Words in a segment divided by its length in minutes (`end` minus `start`). Report the range across segments, not only the mean. Short segments give noisy numbers.
- **Uptalk.** A rising pitch at the end of a statement. In a span, compare `pitchHz` of the last voiced frames with the frames before them (`pitchPercentilesHz` gives the usual range). Count it only on statements, not on questions.
- **Fillers.** Count filler words in the `text` of the user's segments ("um", "uh", "like", "you know", "so", and the equivalents in the meeting language). Give the count per minute of the user's speaking time.
- **Interruptions.** A segment of one speaker that starts before the previous segment of another speaker has ended (`start` less than the earlier `end`). Say who started speaking over whom, and how often. Overlap of one or two seconds is often normal turn-taking.

When you quote the user, use the `text` field as it is and give the `start` time of the segment.
