# 封面图设计指南

## 生图工具优先级

1. **Seedream 5.0 Lite**（优先）：`<WORKSPACE>/scripts/seedream-generate.sh`，0.22元/张，无水印
2. **nano-banana-pro**（备选）：Gemini 免费层级，需去水印，额度可能耗尽
3. **HTML 截图**（兜底）：精确控制布局时使用

## 尺寸

- 比例 2.35:1（横版，适配公众号封面）
- Seedream 最小像素要求 ≥ 3686400，推荐 `2560x1440`(16:9) 生成后裁剪为 2.35:1
- nano-banana-pro 建议实际尺寸 900×383 或更大

## 配色方案

| 内容类型 | 配色 | 色彩代码 | 视觉元素 |
|---------|------|---------|---------|
| AI 产品拆解 | 蓝紫渐变 | #1a1f5c → #7c3aed | 产品 logo 元素、拆解感 |
| 场景解决方案 | 绿橙渐变 | #10b981 → #f97316 | 场景图标、流程感 |
| 效率提升实战 | 橙黄渐变 | #f97316 → #eab308 | 工具图标、速度感 |
| 产品方法论 | 深蓝渐变 | #1e3a5f → #3b82f6 | 思维导图感、结构化 |
| 行业观察 | 蓝绿渐变 | #0891b2 → #06b6d4 | 趋势箭头、新闻感 |

## 布局规则

- 左右分区：左 40% 文字，右 60% 视觉元素
- 文字区：主标题（大字加粗）+ 副标题（小字）
- 视觉区：与主题相关的 3D 元素、图标、光效
- 文字和视觉不重叠

## Prompt 模板

### Seedream 5.0 Lite（优先）

```bash
# 生成 16:9 封面，再裁剪为 2.35:1
<WORKSPACE>/scripts/seedream-generate.sh \
  "专业公众号封面图，主题[主题]。[配色]渐变背景。左侧40%放大号中文标题「[标题]」和副标题「[副标题]」，右侧60%放[视觉元素]，现代3D风格图标。干净设计，文字和视觉不重叠。横版，高质量。" \
  cover.jpg "2560x1440" 1
# 裁剪为 2.35:1
sips -c 1090 2560 cover.jpg
```

### nano-banana-pro（备选）

```
A professional WeChat article cover image about [主题].
[配色] gradient background.
Layout: split into two zones — left 40% for text, right 60% for visuals.
Left zone: title "[中文标题]" in bold, subtitle "[中文副标题]" below.
Right zone: [视觉元素描述], modern 3D style icons and elements.
Clean design, no text overlap with visual elements.
Aspect ratio 2.35:1, high quality.
```

## 文字要求

- 标题：中文，6-12 字，加粗醒目
- 副标题：中文，一句话核心价值
- 字体清晰可读，不要艺术字
- ⚠️ **不要用 emoji**：浏览器截图时 emoji 会变成色块。用纯文字 + SVG 几何图形替代

## 质量检查

- [ ] 中文文字清晰可读
- [ ] 颜色鲜明，吸引眼球
- [ ] 主题契合文章内容
- [ ] 视觉和文字不重叠

---

## 内容结构图（推荐）

放在文章开头、封面图之后，帮读者一图看全文。

### 风格

Graphic Recording / Visual Thinking 手绘风格：
- 白纸背景，无横线
- 黑色细线笔轮廓 + 彩色标记（青色、橙色、柔和红色）
- 放射状布局，箭头连接
- 手写体大写字母（英文部分）
- 16:9 比例

### Prompt 模板

```
Create a hand-drawn sketch visual summary about [文章主题].
Clean white paper background, no lines.
Art style: graphic recording / visual thinking.
Black fine-tip pen for outlines and text.
Colored markers (cyan, orange, soft red) for emphasis.
Main title "[文章标题]" centered in a 3D rectangular box.
Surround with radially distributed simple doodles, icons, and diagrams:
- [要点1]
- [要点2]
- [要点3]
Connect ideas with arrows. Clear hand-written block letters.
Layout 16:9, high quality.
```

### 决策规则

- 文章 ≥ 3 个主要观点：建议生成
- 文章内容简单或时间紧迫：可跳过

---

## 正文配图决策

```
有数据对比（性能/价格/用户量）→ 生成对比柱状图
有技术架构（系统组件/数据流）→ 生成架构示意图
有流程步骤（≥5步）→ 生成流程图
其他 → 不生成配图
```

正文配图数量：0-2 张，宁缺毋滥。
