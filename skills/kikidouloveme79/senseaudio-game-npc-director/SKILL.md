---
name: senseaudio-game-npc-director
description: Use when a game, interactive story, or virtual world needs reusable NPC voice behavior, including fixed voice identity, catchphrases, relationship-aware dialogue, player voice intake through SenseAudio ASR, task briefings, narration, and event announcements synthesized with SenseAudio.
---

# SenseAudio Game NPC Director

## What this skill is for

This skill is for building **low-cost, high-immersion voice assets** for games and interactive worlds.

It treats voice as part of the world model, not just a final rendering step.

You can use it to give each NPC:

- a fixed voice
- a role or class identity
- catchphrases
- relationship-aware tone shifts
- event-based spoken lines
- ASR-driven reactions to what the player actually says

## Strong use cases

### 1. Quest and task broadcasters

Generate:

- new quest lines
- reminder lines
- completion lines
- failure or delay lines

with one consistent NPC voice.

### 2. Relationship-aware NPC dialogue

Use the same NPC voice but adjust line style based on:

- stranger
- neutral
- trusted
- close ally

This makes the world feel reactive without needing fully hand-authored voice libraries.

### 3. Player voice intake

Use SenseAudio ASR to transcribe a player's spoken line, then generate a relation-aware NPC reply.

This is the bridge from:

- static voiced assets

to:

- interactive voiced worlds

### 4. Dynamic world event announcements

Generate voiced lines for:

- invasion warnings
- weather changes
- market events
- faction alerts
- town broadcasts

### 5. Worldbuilding narration

Generate short lore or ambient narration using one narrator voice or one faction-specific voice.

## Workflow

1. Define the NPC profile:
   - name
   - role
   - world
   - speaking style
   - catchphrase
   - default `voice_id`
2. Choose one of two paths:
   - scene-first: define an event and generate NPC lines directly
   - player-first: transcribe player audio with `scripts/senseaudio_asr.py`, then build NPC reply lines from the transcript
3. Define the current scene:
   - event type
   - player relationship
   - player state
   - objective
4. Run either `scripts/build_npc_scene_manifest.py` or `scripts/build_npc_reply_from_player.py`.
5. Review the generated lines.
6. Run `scripts/batch_tts_scene.py` with the fixed `voice_id`.
   - If you already created a clone on the SenseAudio platform, use that prepared clone `voice_id`.
   - A prepared cloned voice id commonly looks like `vc-...`, and can be passed directly with `--clone-voice-id`.
   - This skill already uses streaming TTS internally and now records stream chunk metadata.
   - If the chosen voice is a clone id like `vc-...`, scene synthesis now auto-routes to `SenseAudio-TTS-1.5`.
7. If the user wants to hear the NPC lines directly in Feishu or PicoClaw, run `scripts/send_npc_scene_to_feishu.py`, or add `--send-feishu-audio` to `scripts/run_player_voice_npc_pipeline.py`.
   - This step reuses the same Feishu audio delivery path as the dedicated voice-reply skill.
   - It transcodes the generated `.mp3` lines into `.ogg/.opus` and sends them one by one as real `audio` messages.
8. Attach the resulting assets to your runtime, editor tooling, or content review flow.

## OpenClaw Or PicoClaw Trigger Pattern

Use this skill as a mode-based session.

Recommended user trigger:

```text
进入 NPC 模式，用 $senseaudio-game-npc-director。
NPC：雾港档案官阿砚
关系：trusted
地点：北码头
目标：找回失踪账册
clone voice_id：your_clone_voice_id
后面我发语音，你都按这个设定回复。
```

After mode entry, the agent should keep session state with:

- npc identity
- relationship
- location
- objective
- chosen `voice_id`

For each new player turn:

1. If the input is audio, transcribe it with `scripts/senseaudio_asr.py` or `scripts/run_player_voice_npc_pipeline.py`.
2. Generate the NPC reply.
3. Synthesize the reply with the fixed voice.
4. If the user says "直接发语音" or "一条一条发 NPC 语音", use `--send-feishu-audio` so the generated NPC lines are sent one by one as Feishu `audio` messages.
5. Return both text and audio when the channel supports voice playback.

If the user asks to switch voice, only swap the configured `voice_id`; keep the same NPC profile and relationship state.

## Design rules

- Keep one NPC tied to one stable voice wherever possible.
- Let emotion and relation change the wording, not the identity.
- Use short lines for reactive NPC speech and system announcements.
- For player voice loops, make ASR intake deterministic before adding deeper agent logic.
- If you want faster perceived NPC response generation, use stream ASR for the player-input leg.
- Treat cloned voices or exclusive voices as drop-in replacements for the same workflow.
- Official clone support is a two-step chain:
  - create the clone on the SenseAudio platform first
  - then use the prepared clone `voice_id` here

## Resources

- `scripts/build_npc_scene_manifest.py`
  - Builds scene lines from an NPC profile and game state
- `scripts/senseaudio_asr.py`
  - Calls SenseAudio ASR using the official open API host or the official platform endpoint
  - Defaults to the official `sense-asr-deepthink` model
- `scripts/build_npc_reply_from_player.py`
  - Turns a player transcript into intent-aware NPC reply lines
- `scripts/run_player_voice_npc_pipeline.py`
  - Runs the full player voice pipeline end to end
  - Supports `--stream-asr`, `--clone-voice-id`, and `--send-feishu-audio`
- `scripts/batch_tts_scene.py`
  - Synthesizes all scene lines with one fixed voice
- `scripts/send_npc_scene_to_feishu.py`
  - Reuses the Feishu voice delivery path to send generated NPC lines one by one as audio messages
- `references/npc_voice_design.md`
  - Patterns for worldbuilding, relation states, and event announcements
- `references/asr_player_loop.md`
  - Official ASR findings and the recommended player voice pipeline
