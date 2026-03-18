# Suno API 参考资料

Suno AI 音乐生成 API 文档。

## 简介

Suno 是一个 AI 音乐生成平台，可以根据文本描述或 MIDI 输入生成高质量音乐。

## API 认证

```python
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
```

## 核心接口

### 生成音乐

```python
import requests

response = requests.post(
    "https://api.suno.ai/v1/generate",
    headers=headers,
    json={
        "melody": base64_encoded_midi,
        "style": "pop",
        "mood": "upbeat",
        "duration": 120,
        "format": "mp3"
    }
)
```

### 查询状态

```python
response = requests.get(
    f"https://api.suno.ai/v1/status/{task_id}",
    headers=headers
)
```

## 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `melody` | string | Base64 编码的 MIDI |
| `style` | string | 音乐风格 |
| `mood` | string | 情绪标签 |
| `duration` | integer | 生成时长（秒） |
| `format` | string | 输出格式 |

## 参考资料

- 官网: https://www.suno.ai/
- API 文档: https://www.suno.ai/docs
