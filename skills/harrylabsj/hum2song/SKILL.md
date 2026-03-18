# Hum2Song Skill

将用户哼唱的旋律转化为完整歌曲（含伴奏、编曲），让每个人都能轻松创作专业级音乐。

## 功能概述

Hum2Song 是一个 AI 驱动的音乐创作工具，能够将用户的哼唱音频转化为完整的歌曲作品。

### 核心能力

- **音频输入处理**：支持 MP3/WAV/M4A/OGG 格式
- **智能音频预处理**：降噪、标准化、格式转换
- **旋律提取**：音高检测、节奏分析、MIDI 生成
- **AI 音乐生成**：集成 Suno API 或 ACE-Step
- **多格式输出**：MP3/WAV/MIDI

## 使用方式

### 方式一：命令行使用

```bash
# 基本使用 - 上传哼唱音频生成歌曲
hum2song generate --input my_humming.mp3

# 指定音乐风格
hum2song generate --input my_humming.mp3 --style pop --mood happy

# 生成带歌词的歌曲
hum2song generate --input my_humming.mp3 --lyrics "歌词内容.txt"

# 批量生成多种风格
hum2song batch --input melody.wav --styles pop,rock,electronic

# 查看任务状态
hum2song status --task-id h2s_20241215_001

# 下载生成结果
hum2song download --task-id h2s_20241215_001 --output ./my_songs/
```

### 方式二：Python API

```python
import hum2song

# 基础生成
result = hum2song.generate(
    audio_path="my_humming.mp3",
    style="pop",
    mood="upbeat"
)

# 高级配置
config = hum2song.Config(
    audio_path="humming_demo.wav",
    style="folk",
    mood="romantic",
    lyrics={
        "enabled": True,
        "text": "月光洒在旧窗台...",
        "language": "zh"
    },
    output_formats=["mp3", "wav", "midi"],
    include_instrumental=True
)

result = hum2song.generate(config)
print(f"歌曲生成完成: {result.full_song_url}")
```

### 方式三：OpenClaw 工具调用

```
# 在 OpenClaw 中直接调用
将这段哼唱转成流行风格的歌曲: /path/to/humming.m4a

# 指定更多参数
用这段音频生成一首欢快的摇滚歌曲，要包含歌词
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `input` | string | 是 | 输入音频文件路径 | - |
| `style` | string | 否 | 音乐风格 | `pop` |
| `mood` | string | 否 | 情绪标签 | `auto` |
| `tempo` | number/string | 否 | BPM 速度 | `auto` |
| `key` | string | 否 | 调性 | `auto` |
| `lyrics` | string | 否 | 歌词文件路径或文本 | - |
| `output_formats` | array | 否 | 输出格式 | `["mp3"]` |
| `include_instrumental` | boolean | 否 | 是否包含伴奏版 | `false` |

### 支持的音乐风格

- `pop` - 流行
- `rock` - 摇滚
- `electronic` - 电子
- `classical` - 古典
- `jazz` - 爵士
- `folk` - 民谣
- `hiphop` - 嘻哈
- `rnb` - R&B

### 支持的情绪标签

- `happy` - 欢快
- `sad` - 悲伤
- `energetic` - 激昂
- `calm` - 平静
- `romantic` - 浪漫
- `epic` - 史诗
- `mysterious` - 神秘

## 输出说明

成功生成后，将返回以下文件：

```json
{
  "task_id": "h2s_20241215_001",
  "status": "completed",
  "outputs": {
    "full_song": {
      "mp3": "/output/h2s_001_full.mp3",
      "wav": "/output/h2s_001_full.wav"
    },
    "instrumental": {
      "mp3": "/output/h2s_001_inst.mp3"
    },
    "midi": "/output/h2s_001.mid",
    "metadata": {
      "bpm": 120,
      "key": "C Major",
      "duration": "2:30",
      "style": "pop"
    }
  }
}
```

## 技术实现

### 核心流程

```
哼唱音频 → 音频预处理 → 旋律提取 → AI 音乐生成 → 混音输出
              ↓              ↓              ↓
           降噪/标准化    音高/节奏检测   Suno/ACE-Step
```

### 技术栈

- **Python 3.10+** - 主开发语言
- **librosa** - 音频分析和特征提取
- **basic-pitch** - 音高检测
- **pretty_midi** - MIDI 文件处理
- **Suno API / ACE-Step** - 音乐生成
- **FFmpeg** - 音频格式转换

### 依赖安装

```bash
pip install hum2song

# 或从源码安装
git clone https://github.com/example/hum2song.git
cd hum2song
pip install -e .
```

### 环境要求

- Python 3.10 或更高版本
- FFmpeg（系统依赖）
- 至少 4GB 内存
- 推荐使用 GPU 加速（可选）

## 配置说明

### 配置文件位置

```
~/.config/hum2song/config.yaml
```

### 配置示例

```yaml
# API 配置
suno:
  api_key: "your-suno-api-key"
  base_url: "https://api.suno.ai/v1"

# 备选方案
ace_step:
  enabled: true
  model_path: "~/.models/ace-step"

# 音频处理
audio:
  sample_rate: 44100
  normalize: true
  noise_reduction: true

# 输出设置
output:
  default_formats: ["mp3", "wav"]
  mp3_bitrate: "320k"
  wav_bitdepth: 16
  output_dir: "~/Music/hum2song"

# 日志
logging:
  level: "INFO"
  file: "~/.logs/hum2song.log"
```

### 环境变量

| 变量名 | 说明 |
|--------|------|
| `HUM2SONG_SUNO_API_KEY` | Suno API 密钥 |
| `HUM2SONG_OUTPUT_DIR` | 默认输出目录 |
| `HUM2SONG_LOG_LEVEL` | 日志级别 |

## 错误处理

### 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `INVALID_FILE_FORMAT` | 不支持的文件格式 | 转换为 MP3/WAV 后重试 |
| `AUDIO_QUALITY_TOO_LOW` | 音频质量过低 | 在安静环境重新录制 |
| `NO_MELODY_DETECTED` | 未检测到旋律 | 哼唱更清晰的旋律 |
| `GENERATION_FAILED` | 生成失败 | 检查 API 配置或稍后重试 |
| `TIMEOUT` | 处理超时 | 简化旋律或稍后重试 |

### 质量建议

为获得最佳效果，建议：

1. **录制环境**：选择安静环境，避免背景噪音
2. **录制距离**：距离麦克风 10-20 厘米
3. **旋律时长**：推荐 30 秒 - 2 分钟
4. **哼唱方式**：保持稳定的音准和节奏
5. **音频格式**：优先使用 WAV 或高质量 MP3

## 使用示例

### 示例 1：快速创作流行歌曲

```bash
# 上传哼唱，自动生成流行歌曲
hum2song generate --input my_melody.m4a --style pop --mood happy

# 输出：
# ✓ 音频上传成功
# ✓ 检测到 BPM: 128, 调性: C Major
# ✓ 生成中...
# ✓ 完成！输出文件: ./my_melody_pop.mp3
```

### 示例 2：创作带歌词的民谣

```python
import hum2song

result = hum2song.generate(
    audio_path="humming.wav",
    style="folk",
    mood="romantic",
    lyrics={
        "enabled": True,
        "text": """月光洒在旧窗台
回忆像风轻轻吹
那些年少时的梦啊
如今都飞向何方""",
        "language": "zh"
    },
    output_formats=["mp3", "wav", "midi"]
)

print(f"完整版: {result['outputs']['full_song']['mp3']}")
print(f"伴奏版: {result['outputs']['instrumental']['mp3']}")
print(f"MIDI: {result['outputs']['midi']}")
```

### 示例 3：批量生成多种风格

```bash
# 创建风格配置文件
cat > styles.json << 'EOF'
{
  "variations": [
    {"style": "pop", "mood": "upbeat"},
    {"style": "rock", "mood": "energetic"},
    {"style": "electronic", "mood": "mysterious"}
  ]
}
EOF

# 批量生成
hum2song batch --input base_melody.mp3 --config styles.json --output ./demos/

# 查看结果
ls ./demos/
# base_melody_pop_upbeat.mp3
# base_melody_rock_energetic.mp3
# base_melody_electronic_mysterious.mp3
```

## 注意事项

1. **API 配额**：使用 Suno API 需要有效的 API 密钥，注意配额限制
2. **处理时间**：生成一首歌曲通常需要 30-120 秒
3. **版权问题**：生成的音乐版权归属请参考 Suno API 服务条款
4. **隐私保护**：上传的音频仅用于生成音乐，不会被存储或用于其他用途

## 故障排查

### 检查安装

```bash
hum2song doctor
```

### 测试音频质量

```bash
hum2song analyze --input my_audio.mp3
```

### 查看日志

```bash
tail -f ~/.logs/hum2song.log
```

## 相关资源

- [Basic Pitch 文档](https://github.com/spotify/basic-pitch)
- [Librosa 文档](https://librosa.org/doc/latest/)
- [Suno API 文档](https://www.suno.ai/)
- [ACE-Step 项目](https://github.com/ace-step/ace-step)

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2024-12 | 初始版本，支持核心功能 |

## 许可证

MIT License
