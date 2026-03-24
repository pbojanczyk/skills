---
name: summarize-all
description: "✨ 智能总结工具 - 自动检测内容类型、智能选择长度、缓存、关键点提取。支持网页、PDF、图片、音频、YouTube。"
---

# ✨ Summarize All Pro

**Advanced AI Smart Summarizer v2.5**

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Stream Output** | Typewriter effect, real-time display |
| 📝 **Markdown Render** | Pretty formatted output |
| 🔍 **History Search** | Search through summaries |
| 📚 **Batch Mode** | Process multiple URLs |
| 🔔 **Notifications** | Desktop alerts on completion |
| ⚖️ **Compare Mode** | Compare multiple articles |
| 🔎 **Keyword Tracking** | Alert on keyword mentions |
| 🏷️ **Auto Tags** | Automatic content tagging |
| 📑 **PDF Merge** | Combine and summarize PDFs |
| 🎓 **Academic Mode** | Specialized paper analysis |

## Commands

```bash
# Basic
summarize-all <url>

# Batch
summarize-all batch urls.txt
cat urls.txt | summarize-all batch -

# Compare
summarize-all compare url1 url2 [url3...]

# Academic
summarize-all academic paper.pdf

# Search
summarize-all search "keyword"

# Tags
summarize-all tags

# Keywords
summarize-all keywords add "AI" "New development"
summarize-all keywords list

# API Server
summarize-all server 8080
```

## Options

- `--length, -l` short/medium/long/xl/auto
- `--lang, -L` en/zh/ja/ko/fr/de/es/auto
- `--verbose, -v` Verbose output
- `--no-cache` Skip cache

## Config

```bash
summarize-all config set endpoint <url>
summarize-all config set key <key>
summarize-all config set model <model>
```
