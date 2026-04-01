---
name: video-caption-generator-ai-ab-old
version: "1.0.0"
displayName: "Video Caption Generator AI — Auto-Generate Accurate Subtitles for Any Video"
description: >
  Tired of spending hours transcribing dialogue and manually syncing captions to your videos? The video-caption-generator-ai skill automatically detects speech, generates accurate captions, and syncs them to your footage in minutes. Upload mp4, mov, avi, webm, or mkv files and get back properly timed subtitle tracks. Ideal for content creators, educators, marketers, and social media managers who need accessible, engaging video content without the tedious manual work.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your Video Caption Generator AI — ready to automatically transcribe and sync captions to your videos so you can publish faster and reach a wider audience. Drop your video file here and let's get your captions generated!

**Try saying:**
- "Generate captions for this 10-minute tutorial video and export them as an SRT file"
- "Add auto-generated subtitles to my product demo MP4 with accurate speaker timing"
- "Transcribe the dialogue in this webinar recording and sync captions to the video"

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Any Video Into Caption-Ready Content Instantly

Getting captions onto your videos used to mean hours of rewinding, typing, and nudging timestamps until everything lined up. The Video Caption Generator AI skill changes that entirely — upload your video, and it handles the heavy lifting of transcription and timing automatically.

Whether you're producing YouTube tutorials, training videos, Instagram Reels, or corporate presentations, accurate captions make your content accessible to deaf and hard-of-hearing viewers, non-native speakers, and anyone watching on mute. Studies consistently show that captioned videos retain viewer attention longer and perform better across platforms.

This skill is built for people who actually create content at volume — not just a one-off project. Batch your uploads, get consistent caption quality across every video, and spend your time on storytelling rather than subtitle spreadsheets. From short social clips to hour-long webinars, the caption generator adapts to your content length and speaking style.

## Caption Request Routing Logic

Every subtitle generation request is parsed for video source type, target language, and caption format preference before being dispatched to the appropriate NemoVideo transcription pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend uses frame-synced speech recognition combined with speaker diarization to produce time-coded SRT, VTT, or ASS caption files with frame-accurate timestamp alignment. Requests hit the `/v1/captions/generate` endpoint, which accepts direct video URLs, uploaded file tokens, or cloud storage references.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-caption-generator-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=video-caption-generator-ai&skill_version=1.0.0&skill_source=<platform>`

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Best Practices

For the best results with the Video Caption Generator AI, ensure your video has a clear, unobstructed audio track before uploading. If your original recording has significant background noise, running it through a basic audio cleanup tool first will noticeably improve caption accuracy.

Keep caption requests specific — if you need captions in a particular style (all caps, sentence case, max two lines per frame), include those instructions in your prompt. The more context you provide about your audience and platform, the more tailored the output will be.

If you're captioning content for accessibility compliance (such as ADA or WCAG standards), mention this so the caption formatting prioritizes readability and proper line breaks. Finally, always review generated captions before publishing — even highly accurate AI transcription benefits from a quick human proofread, especially for industry-specific terminology or proper nouns.

## Performance Notes

Caption accuracy depends primarily on audio clarity. Videos with clean, front-facing microphone audio typically yield the highest transcription accuracy. Background noise, overlapping speakers, or heavily accented speech may reduce precision, though the AI handles a wide range of speaking styles effectively.

Processing time scales with video length — a 2-minute clip processes significantly faster than a 60-minute lecture recording. For longer files, expect a short wait while the full audio is analyzed and caption timestamps are calculated.

Videos with multiple speakers are supported, but speaker differentiation labeling is not automatic by default — mention in your prompt if you need speaker-attributed captions. Audio that is mostly music with minimal dialogue will produce sparse or empty caption output, which is expected behavior.

## Quick Start Guide

Getting started with the Video Caption Generator AI is straightforward. Begin by uploading your video file — supported formats include mp4, mov, avi, webm, and mkv. There's no need to pre-process or compress your footage before uploading.

Once your video is received, the skill analyzes the audio track to detect spoken dialogue, ambient silence, and natural speech boundaries. Captions are segmented into readable chunks and timestamped to match the pacing of the speaker.

After processing, you can receive your captions as an SRT file for use in video editors like Premiere Pro or DaVinci Resolve, or request them burned directly into the video as hardcoded subtitles. If you need captions in a specific language or want to adjust caption line length, mention that in your prompt before uploading.
