---
name: video-splitter
version: "1.0.0"
displayName: "Video Splitter — Split, Segment and Divide Videos into Clips Automatically with AI"
description: >
  Split any video into multiple clips automatically using AI scene detection, silence detection, or custom timestamps. NemoVideo divides long recordings into shareable segments, detects scene changes and topic transitions, splits by equal duration or file size for upload limits, extracts the best moments for short-form repurposing, and batch-exports every clip with consistent naming — turning a 60-minute recording into 15 ready-to-post clips without touching a timeline.
metadata: {"openclaw": {"emoji": "✂️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Video Splitter — Split and Segment Videos into Clips Automatically

Long-form content is where the value lives. Short-form content is where the audience lives. The bridge between them is splitting — taking a 60-minute podcast, a 45-minute webinar, a 30-minute lecture, or a 20-minute YouTube video and extracting the 8-15 moments that work as standalone short-form clips on TikTok, Reels, Shorts, and LinkedIn. A human editor doing this manually watches the entire source video at 2x speed (30 minutes for a 60-minute source), identifies clip-worthy moments, sets in/out points, and exports each clip — a process that takes 2-4 hours per source video and produces 8-12 clips if the editor is fast. NemoVideo automates the entire pipeline: it analyzes the source video using scene detection (visual changes), silence detection (pauses between topics), transcript analysis (topic boundaries from what's being said), and energy detection (audience laughter, applause, speaker emphasis) — then generates clips at every identified split point, ranked by predicted engagement. The creator reviews the clips, selects the strongest ones, and posts. The 4-hour editing session becomes a 15-minute review session.

## Use Cases

1. **Podcast → Short-Form Clips (60 min → 10-15 clips)** — A weekly podcast episode. NemoVideo analyzes the transcript, identifies topic changes, and extracts: every story/anecdote (beginning to punchline), every strong opinion (high-energy speech segments), and every quotable moment (sentences under 15 seconds with high confidence scores). Each clip is auto-trimmed to start 0.5 seconds before the first word and end 1 second after the last, with fade-to-black outro. Exported 9:16 with captions for TikTok/Reels.
2. **Webinar → Chapter Segments (45 min → 5-8 chapters)** — A recorded webinar for a SaaS company. NemoVideo splits at topic transitions: intro, problem statement, demo section 1, demo section 2, Q&A, and closing CTA. Each chapter exported as a standalone video with title card, for the company's learning library and YouTube chapters.
3. **Lecture Recording → Study Segments (90 min → 12-15 segments)** — A university professor's recorded lecture. NemoVideo detects slide changes (visual scene detection) and splits at each new slide topic. Each segment becomes a study module: titled by the slide heading, trimmed of transition dead-time, and chaptered for the LMS platform.
4. **Gaming Stream → Highlight Clips (3 hours → 20 clips)** — A Twitch stream. NemoVideo identifies: kill moments (crowd/audio energy spikes), funny reactions (laughter detection), clutch plays (rapid input followed by energy spike), and raid/donation moments (on-screen alert detection). Each clip: 15-60 seconds, auto-titled by game moment, exported for YouTube Shorts and TikTok.
5. **Equal-Duration Split for Upload Limits** — A 2-hour training video needs to be uploaded to a platform with a 15-minute file limit. NemoVideo splits into 8 equal segments of 15 minutes each, with 2-second overlap at each boundary (so viewers don't miss content at split points), sequentially numbered, and each segment opens with a "Part X of 8" title card.

## How It Works

### Step 1 — Upload Source Video
Provide the long-form video. NemoVideo accepts any length — from 5 minutes to 8+ hours. All major formats supported.

### Step 2 — Choose Split Method
Select: scene detection (visual), silence detection (audio gaps), transcript analysis (topic boundaries), energy detection (engagement peaks), equal duration, or custom timestamps.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "video-splitter",
    "prompt": "Split a 55-minute podcast episode into short-form clips for TikTok and Reels. Use transcript analysis to find: (1) complete stories/anecdotes from beginning to punchline, (2) strong opinions with emotional emphasis, (3) quotable one-liner moments under 15 seconds. Target clip length: 30-90 seconds each. Trim each clip to start 0.5 sec before first word and end 1 sec after last word. Add 1-second fade-to-black at end of each clip. Export each clip as separate 9:16 MP4 with auto-captions (bold white, black outline). Rank clips by predicted engagement score.",
    "split_method": "transcript-analysis",
    "clip_length": "30-90 sec",
    "captions": true,
    "fade_out": true,
    "rank_by": "engagement-prediction",
    "format": "9:16"
  }'
```

### Step 4 — Review Ranked Clips and Publish
NemoVideo presents all clips ranked by predicted engagement. Preview the top 5, select the best 3-5 for immediate posting, and schedule the rest across the week.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the source video and splitting requirements |
| `split_method` | string | | "scene-detection", "silence-detection", "transcript-analysis", "energy-detection", "equal-duration", "custom-timestamps" |
| `clip_length` | string | | Target range: "15-60 sec", "30-90 sec", "5-15 min" |
| `timestamps` | array | | Custom split points: ["0:00", "5:32", "12:15", "18:40"] |
| `equal_segments` | integer | | Number of equal-duration segments |
| `captions` | boolean | | Auto-caption each clip (default: false) |
| `fade_out` | boolean | | Add fade-to-black at clip end (default: true) |
| `title_cards` | boolean | | Add title card with clip topic at start (default: false) |
| `rank_by` | string | | "engagement-prediction", "energy-level", "chronological" |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "vspl-20260328-001",
  "status": "completed",
  "source_duration_minutes": 55,
  "clips_generated": 14,
  "clips": [
    {
      "clip": 1,
      "title": "Why I Quit My $300K Job",
      "start": "04:22",
      "end": "05:48",
      "duration_seconds": 86,
      "engagement_score": 0.94,
      "type": "story-anecdote",
      "file": "clip-01-quit-job.mp4"
    },
    {
      "clip": 2,
      "title": "The Worst Career Advice I Ever Got",
      "start": "12:05",
      "end": "13:12",
      "duration_seconds": 67,
      "engagement_score": 0.91,
      "type": "strong-opinion",
      "file": "clip-02-worst-advice.mp4"
    },
    {
      "clip": 3,
      "title": "Nobody Tells You This About Startups",
      "start": "28:40",
      "end": "29:22",
      "duration_seconds": 42,
      "engagement_score": 0.88,
      "type": "quotable-moment",
      "file": "clip-03-startup-truth.mp4"
    }
  ],
  "split_stats": {
    "method": "transcript-analysis",
    "topics_detected": 8,
    "energy_peaks": 22,
    "clips_ranked": 14
  }
}
```

## Tips

1. **Transcript analysis produces the best podcast clips** — Scene detection is useless on a static two-camera podcast. Transcript analysis finds topic boundaries and complete stories that make sense as standalone clips.
2. **Energy detection finds viral moments** — Laughter, raised voices, dramatic pauses, and rapid speech indicate emotionally charged content. These moments have the highest share probability on short-form platforms.
3. **30-90 seconds is the clip sweet spot** — Under 15 seconds lacks context. Over 90 seconds loses short-form audiences. NemoVideo targets this range by default for social repurposing.
4. **Overlap at split boundaries prevents information loss** — For sequential viewing (lecture parts), 2-second overlaps ensure the viewer doesn't miss a sentence at the cut point.
5. **Batch-export with consistent naming saves hours** — `clip-01-topic.mp4`, `clip-02-topic.mp4` with auto-generated titles from transcript topics. Import directly to scheduling tools.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts clips |
| MP4 16:9 | 1920x1080 | YouTube chapters / website |
| MP4 1:1 | 1080x1080 | LinkedIn / Twitter / Facebook |
| CSV manifest | — | Clip list with timestamps, titles, scores |

## Related Skills

- [auto-caption-video](/skills/auto-caption-video) — Add captions to clips
- [video-cropper](/skills/video-cropper) — Reframe clips per platform
- [speed-ramp-video](/skills/speed-ramp-video) — Add speed effects to clips
