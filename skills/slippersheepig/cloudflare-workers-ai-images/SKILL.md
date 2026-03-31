---
name: cloudflare-workers-ai-image
description: Generate and edit images through Cloudflare Workers AI using one skill that supports text-to-image and image-to-image. Use when the user asks to generate, draw, create, render, transform, restyle, or modify images with Cloudflare Workers AI models such as stable-diffusion-xl-base-1.0 and stable-diffusion-v1-5-img2img. Trigger for requests about prompt-based image generation, editing an existing image, preserving a source image while changing overall style or composition, or when the user explicitly mentions Cloudflare Workers AI, Workers AI, SDXL, or img2img.
---

# Cloudflare Workers AI Image

Use this skill for two related image workflows backed by Cloudflare Workers AI:

- **text2img** → create a new image from a prompt
- **img2img** → transform an existing source image with a prompt

Use the bundled script:

```bash
python3 scripts/cf_workers_ai_image.py <mode> "<prompt>" [options]
```

The script reads credentials from environment variables so the skill works cleanly in Docker-based OpenClaw deployments.

## Trigger guidance

Use this skill when the user wants any of the following through Cloudflare Workers AI:

- generate a brand-new image from text
- make a picture, illustration, concept art, poster, wallpaper, avatar, or cover image
- transform an existing image into another style or composition
- keep the original image as a base but restyle or modify it globally
- perform text2img or img2img with Stable Diffusion-family models on Cloudflare

Strong trigger phrases include:

- "用 Cloudflare Workers AI 生成图片"
- "用 Workers AI 做文生图"
- "用 SDXL 生成一张图"
- "把这张图改成水彩风"
- "基于这张图重绘"
- "用 img2img 改图"
- "用 Workers AI 改这张图片风格"

Mode selection guidance:

- Choose **text2img** when there is no source image and the user wants a new image from a prompt.
- Choose **img2img** when there is a source image and the user wants a global transformation, style transfer, or composition-preserving edit.

If the user asks for a local area edit, object replacement, or mask-based redraw, this skill does not cover that workflow anymore.

## Required environment variables

Read `references/docker-compose-env-example.md` when the user asks how to pass credentials through Docker Compose.

Required variables:

- `CF_ACCOUNT_ID`
- `CF_API_TOKEN`

If either variable is missing, the script exits with a clear error.

## Default models

The script defaults to these Workers AI model identifiers:

- `text2img` → `@cf/stabilityai/stable-diffusion-xl-base-1.0`
- `img2img` → `@cf/runwayml/stable-diffusion-v1-5-img2img`

Override any default with `--model` if Cloudflare changes naming or the user wants another compatible Workers AI model.

## Commands

### 1) Text to image

```bash
python3 scripts/cf_workers_ai_image.py text2img "a cozy cabin in snowy mountains, cinematic lighting" --output ./output
```

Optional knobs:

```bash
python3 scripts/cf_workers_ai_image.py text2img "a cozy cabin in snowy mountains, cinematic lighting" \
  --negative-prompt "blurry, low quality, distorted" \
  --num-steps 30 \
  --guidance 7.5 \
  --width 1024 \
  --height 1024 \
  --seed 42 \
  --output ./output
```

### 2) Image to image

```bash
python3 scripts/cf_workers_ai_image.py img2img "turn this into a watercolor illustration" \
  --image ./input/source.png \
  --strength 0.65 \
  --output ./output
```

The bundled script sends the source image as a base64 field (`image_b64`) for Workers AI compatibility.

## Chat workflow

When the user asks for an image result:

1. Decide whether the request is text2img or img2img.
2. Convert the request into one prompt string.
3. Run the bundled script with the correct mode.
4. Save the output locally.
5. Send the generated image back to the current chat whenever supported.
6. If the API returns JSON or an HTTP error, show the exact error instead of claiming success.

## Auto-send workflow for the current chat

When the runtime supports sending local image files back to the active conversation, prefer this flow:

1. Generate the image with `scripts/cf_workers_ai_image.py`.
2. Capture the printed output path from stdout.
3. Send that local file back to the current chat using the platform message/file-send tool.
4. Include a short caption describing whether the result came from text2img or img2img.
5. If direct file delivery fails, fall back to replying with the saved file path and the error.

Recommended captions:

- text2img → `按你的提示生成好了。`
- img2img → `按你的源图和提示改好了。`

If the request is iterative, mention what changed in the new version, such as style, prompt emphasis, or source-image guidance.

## Parameters

- `mode`: `text2img` | `img2img`
- positional `prompt`: prompt text
- `--image`: required for `img2img`
- `--output`: output file path or directory; defaults to `./output`
- `--model`: optional model override
- `--negative-prompt`: optional negative prompt
- `--num-steps`: optional sampling steps
- `--guidance`: optional guidance scale
- `--strength`: optional transformation strength
- `--width`, `--height`: optional text2img dimensions when supported by the model
- `--seed`: optional seed
- `--timeout`: HTTP timeout in seconds

## Smoke testing

Run the bundled smoke test script after changing the API script or credentials:

```bash
python3 scripts/smoke_test.py
```

What it does:

- checks `CF_ACCOUNT_ID` and `CF_API_TOKEN`
- creates a local PNG input for img2img
- runs one `text2img` request
- runs one `img2img` request
- verifies that each command returns a file path and that the output file exists and is non-empty
- prints a JSON summary and exits non-zero if any mode fails

Use smoke tests to validate connectivity and gross regressions, not image quality.

## Troubleshooting

### Missing credentials

If the script says a required environment variable is missing, pass `CF_ACCOUNT_ID` and `CF_API_TOKEN` through Docker Compose. See `references/docker-compose-env-example.md`.

### JSON instead of image

Workers AI may return JSON for errors or validation failures. Surface the full JSON body.

### 401 / 403

The token is missing, invalid, expired, or does not have the right Cloudflare account permission.

### 404 / model not found

Cloudflare may have changed model identifiers. Retry with `--model` using the current Workers AI model name.

### Input image issues

Use PNG for source images when possible.

## Resource

### scripts/cf_workers_ai_image.py

Use this script for deterministic, repeatable Cloudflare Workers AI image generation and editing.

### scripts/smoke_test.py

Use this script for a fast end-to-end connectivity and output smoke test across the supported modes.
