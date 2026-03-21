# Easy-xiaohongshu - 小红书 AI 图文自动发布

✨ 从创意到发布，全自动完成 — 提示词优化 → 图文生成 → 一键发布

## 核心能力

- 🤖 **智能提示词优化** — 根据账号定位自动匹配最佳风格（13种预设）
- 📝 **图文生成** — 文案 + 排版 + AI成品图，一站式完成
- 📱 **自动发布** — 通过 MCP 服务一键发布到小红书
- 📋 **发布文案生成** — 自动生成标题 + 正文 + 标签

## 快速开始

### Step 1：获取 API Key

1. 在 [z.3i0.cn](https://z.3i0.cn/) 注册账号
2. 在钱包管理中按需充值（生图有成本，最低 0.2 元/张）
3. 在令牌管理中点击【添加令牌】
4. 输入名称等信息后保存
5. 复制生成的 API Key

### Step 2：配置 API Key

把以下内容发给龙虾（替换括号里的内容）：

> Easy-xiaohongshu 的 API Key 是【你刚复制的key】
> 我的小红书账号类型是【漫画博主/学习博主/美妆博主等】
> 请帮我把apikey写入配置，并记住我的偏好。

龙虾会自动帮你配置好，并记住你的偏好。

### Step 3：发送创作主题

> 我想发一篇主题为【xxxxxx】的小红书，帮我制作内容

### Step 4：确认文案

龙虾会同时生成图文方案和发布文案（标题+正文+标签），确认没问题后进入下一步。

### Step 5：确认图片

8 张成品图会逐张生成并发给你预览，确认效果后进入下一步。

### Step 6：发布到小红书

龙虾会通过 MCP 服务自动发布。首次使用需要扫码登录，之后无需重复登录。发布前会再次确认。

## 自动发布（可选）

发布功能需要 `xiaohongshu-mcp` 服务，参考 [xhs-mac-mcp](https://clawhub.ai) 技能安装。

## 支持的风格预设

| 账号类型 | 风格 | 适合场景 |
|----------|------|----------|
| 科技博主 | 极简科技感 | AI工具、数码测评 |
| 亲子博主 | 温馨插画风 | 育儿经验、亲子互动 |
| 美妆博主 | 高级ins风 | 护肤教程、彩妆分享 |
| 健身博主 | 活力运动风 | 健身计划、减脂塑形 |
| 美食博主 | 治愈系 | 家常菜、美食探店 |
| 学习博主 | 清新简约 | 学习方法、考试经验 |
| 旅行博主 | 电影感 | 旅行攻略、风景摄影 |
| 职场博主 | 商务简约 | 职场技能、时间管理 |
| 漫画博主 | 热血漫画风 | 动漫解析、漫画推荐 |
| 摄影博主 | 胶片质感 | 摄影教程、作品分享 |
| 穿搭博主 | 时尚杂志风 | 穿搭分享、OOTD |
| 游戏博主 | 电竞科技风 | 游戏攻略、测评 |
| 音乐博主 | 唱片封面风 | 歌单推荐、音乐分享 |

## 文件结构

```
Easy-xiaohongshu/
├── SKILL.md
├── README.md
├── install.sh
├── requirements.txt
├── config/default-config.json
├── scripts/optimize_prompt.py
├── scripts/generate_content.py
├── scripts/generate_image.py
├── scripts/publish_to_xhs.py
├── scripts/publish.sh
└── references/prompt-template.md, caption-template.md, style-presets.json, hashtag-library.json
```

## 依赖

| 依赖 | 用途 | 必需 |
|------|------|------|
| Python 3.8+ | 脚本运行 | ✅ |
| requests | HTTP 请求 | ✅ |
| Z3i0 API | 图像生成 | ✅ |
| xiaohongshu-mcp | 自动发布 | 发布时必需 |

## 许可证

MIT License
