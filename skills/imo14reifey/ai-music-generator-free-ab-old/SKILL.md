---
name: ai-music-generator-free-ab-old
version: "1.0.0"
displayName: "AI Music Generator Free — Create Original Soundtracks for Any Video Instantly"
description: >
  Tired of searching royalty-free music libraries only to find tracks that don't quite fit your video's mood? The ai-music-generator-free skill creates original, custom music tailored to your content — no licensing headaches, no subscription walls. Upload your video (mp4, mov, avi, webm, or mkv) and describe the vibe you want: upbeat corporate, cinematic drama, lo-fi chill, or anything in between. Ideal for YouTubers, social media creators, filmmakers, and marketers who need unique audio fast.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! 🎵 Ready to give your video the perfect original soundtrack? With the AI Music Generator Free skill, just upload your clip and tell me the mood or style you're going for — I'll compose something made specifically for your content. Let's make your video sound as good as it looks!

**Try saying:**
- "Generate a calm, lo-fi background track for my 3-minute meditation video"
- "Create an upbeat, energetic music track that matches the pace of my action sports highlight reel"
- "I need a warm, emotional acoustic piece for a wedding slideshow video — something that builds slowly and feels heartfelt"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Your Videos Deserve Music That Actually Fits

Every video tells a story, and the right music is what makes that story land emotionally. The problem most creators face isn't a lack of music options — it's an overwhelming sea of generic tracks that were never made with their specific content in mind. Stock music libraries give you thousands of choices, but somehow nothing feels right. That's exactly the gap this skill was built to fill.

With the AI Music Generator Free skill, you describe what you need — the energy, the genre, the emotional tone — and it composes an original piece built around your vision. Whether you're editing a travel vlog that needs an adventurous, sweeping score or a product demo that calls for something sleek and modern, the output is music that was made for your moment, not borrowed from someone else's.

This skill is designed for creators at every level. You don't need a music theory background or audio production experience. Just bring your video and your ideas, and let the skill handle the composition. The result is a unique soundtrack you can use freely, without worrying about copyright claims or platform strikes.

## Routing Your Soundtrack Requests

When you describe your video's mood, genre, tempo, or duration, the skill parses those creative parameters and forwards a structured generation prompt directly to the NemoVideo AI music engine.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference Guide

The NemoVideo backend uses a diffusion-based audio synthesis model trained on royalty-free stems, allowing it to generate loopable, tempo-synced tracks in genres ranging from cinematic orchestral to lo-fi beats. Each API call passes your prompt tokens, BPM target, and output duration to return a timestamped audio file ready for immediate video overlay.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-music-generator-free`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=ai-music-generator-free&skill_version=1.0.0&skill_source=<platform>`

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

## Quick Start Guide

Getting started with the AI Music Generator Free skill takes less than a minute. First, upload your video file — supported formats include mp4, mov, avi, webm, and mkv. Once your video is loaded, type a description of the music style you want. Be as specific or as open-ended as you like; the skill works with both.

Next, mention any timing preferences. If your video is 2 minutes long and you want the music to match that duration exactly, say so. If you only need music for a specific segment, describe which part.

Once the track is generated, preview it against your video. If it fits, export and drop it directly into your editing timeline. If you want adjustments, simply describe what to change and request a new version — there's no limit to how many variations you can explore.

For best results on first use, start with a clear genre reference and a rough BPM feel (slow, medium, fast). This gives the skill an immediate framework and typically produces a strong first result without needing multiple rounds of revision.

## Tips and Tricks

The more specific your prompt, the better your music will match your video's tone. Instead of saying 'something upbeat,' try 'fast-paced electronic with punchy beats for a 90-second product launch video.' Describing tempo, instrumentation preferences, and the emotional arc you want (builds up, stays steady, fades out) gives the generator much more to work with.

If your video has distinct sections — like a slow intro that picks up pace mid-way — mention that in your request. You can ask for music that evolves over time rather than staying flat throughout the clip.

Don't overlook genre blending. Some of the most interesting results come from hybrid requests like 'cinematic hip-hop for a city travel montage' or 'acoustic folk with electronic undertones for a startup story video.' The AI Music Generator Free skill handles these nuanced combinations well, so experiment freely.

After generating a track, if the energy is close but not quite right, describe the adjustment: 'a bit less intense in the first 30 seconds' or 'add more bass.' Iterating with small, specific tweaks usually gets you to the perfect result faster than starting over.
