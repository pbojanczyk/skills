# ACE-Step 参考资料

开源音乐生成模型，Suno API 的备选方案。

## 简介

ACE-Step 是一个开源的 AI 音乐生成模型，支持根据 MIDI 或文本描述生成音乐。

## 特点

- 开源免费
- 支持本地部署
- 可自定义训练

## 安装

```bash
# 克隆仓库
git clone https://github.com/ace-step/ace-step.git
cd ace-step

# 安装依赖
pip install -r requirements.txt
```

## 基本用法

```python
from ace_step import MusicGenerator

# 加载模型
generator = MusicGenerator.from_pretrained("ace-step/base")

# 从 MIDI 生成
audio = generator.generate_from_midi(
    midi_path="input.mid",
    style="pop",
    duration=120
)

# 保存
audio.save("output.mp3")
```

## 模型变体

| 模型 | 大小 | 特点 |
|------|------|------|
| `ace-step/base` | 1B | 基础版本 |
| `ace-step/large` | 3B | 高质量版本 |

## 参考资料

- GitHub: https://github.com/ace-step/ace-step
- 论文: https://arxiv.org/abs/xxxx.xxxxx
