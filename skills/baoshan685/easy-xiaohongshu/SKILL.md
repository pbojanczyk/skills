# Easy-xiaohongshu - 小红书 AI 图文自动发布

✨ **零门槛发布小红书图文笔记** - 你提供主题，openclaw完成从文案到图片再到发布全流程

---

## 🎯 核心能力

- 🤖 **智能提示词优化** - 根据账号定位自动匹配最佳风格（13种预设）
- 📝 **图文生成** - 文案 + 排版 + AI成品图，一站式完成
- 🖼️ **AI 图像生成** - 直接生成带中文文案的成品图（逐张生成，实时反馈，支持断点续传）
- 📱 **自动发布** - MCP 服务 → 扫码登录 → 一键发布
- 📋 **发布文案生成** - 自动生成标题 + 正文 + 标签

---

## 📦 安装

```bash
cd ~/.openclaw/skills/Easy-xiaohongshu
bash install.sh
pip3 install -r requirements.txt
```

---

## 🚀 使用流程

### Step 1：获取 API Key

1. 在 [z.3i0.cn](https://z.3i0.cn/) 注册账号
2. 在钱包管理中按需充值（生图有成本，最低 0.2 元/张）
3. 在令牌管理中点击【添加令牌】
4. 输入名称等信息后保存
5. 复制生成的 API Key

### Step 2：配置 API Key

把以下内容发给龙虾（替换括号里的内容）：
```
> Easy-xiaohongshu 的 API Key 是【你刚复制的key】
> 我的小红书账号类型是【漫画博主/学习博主/美妆博主等】
> 请帮我把apikey写入配置，并记住我的偏好。
```
龙虾会自动帮你配置好，并记住你的偏好。

也可以手动编辑 `config/default-config.json`，填写 `api.api_key` 字段。

### Step 3：发送创作主题

```
> 我想发一篇主题为【xxxxxxxx】的小红书，帮我制作内容
```

### Step 4：确认文案

龙虾会同时生成图文方案和发布文案（标题+正文+标签），确认没问题后进入下一步。

### Step 5：确认图片

成品图会逐张生成并发给你预览，确认效果后进入下一步。

### Step 6：发布到小红书

龙虾会通过 MCP 服务自动发布。首次使用需要扫码登录，之后无需重复登录。发布前会再次确认。

---

## 📋 完整流程

```
用户输入主题
   ↓
【Step 1: 提示词优化】
根据账号定位/内容方向/用户对象，匹配最佳风格预设
   ↓
【Step 2: 同时生成图文方案 + 发布文案】
图文方案（多页文案+画面描述）+ 发布文案（标题+正文+标签）
   ↓
【Step 3: 用户确认方案和文案】
展示图文方案 + 发布文案，等待用户确认
   ↓
【Step 4: 生成图片（逐张生成，实时反馈）】
每生成一张立即展示给用户，支持断点续传
   ↓
【Step 5: 用户确认图片】
全部图片生成后，用户确认效果
   ↓
【Step 6: MCP 发布】
检查登录 → 如需扫码则打开二维码 → 上传发布
   ↓
完成 ✅
```

---

## 🎨 支持的风格预设

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

---

## 📁 文件结构

```
~/.openclaw/skills/Easy-xiaohongshu/
├── SKILL.md                          # 技能说明
├── README.md                         # 使用文档
├── install.sh                        # 安装脚本
├── requirements.txt                  # Python 依赖
├── config/
│   └── default-config.json           # API 配置 + 默认参数
├── scripts/
│   ├── optimize_prompt.py            # 提示词优化器
│   ├── generate_content.py           # 文案生成
│   ├── generate_image.py             # 图像生成（支持断点续传）
│   ├── publish_to_xhs.py             # MCP 自动发布脚本
│   └── publish.sh                    # 一键发布入口
└── references/
    ├── prompt-template.md            # 图文提示词模板
    ├── caption-template.md           # 发布文案模板
    ├── style-presets.json            # 13种风格预设
    └── hashtag-library.json          # 标签库（14个类别）
```

---

## ⚙️ 配置说明

配置文件：`config/default-config.json`

```json
{
  "pages": 8,
  "ratio": "3:4",
  "width": 1080,
  "height": 1440,
  "title_max_length": 20,
  "content_min_length": 35,
  "content_max_length": 70,
  "hashtag_count": 8,
  "output_dir": "./generated_images",
  "api": {
    "api_key": "",
    "base_url": "https://z.3i0.cn/v1beta",
    "model": "gemini-3.1-flash-image-preview",
    "timeout_seconds": 120,
    "max_retries": 3
  },
  "mcp": {
    "url": "http://localhost:18060/mcp",
    "timeout_seconds": 30
  }
}
```

API Key 从 `config/default-config.json` 的 `api.api_key` 字段读取。

---

## 🔧 故障排查

### 图片生成失败

```bash
# 检查 API 密钥（优先环境变量，其次配置文件）
cat config/default-config.json | grep api_key

# 测试 API 连接
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://z.3i0.cn/v1beta/models"
```

### 小红书发布失败

```bash
# 检查 MCP 服务是否运行
ps aux | grep xiaohongshu-mcp

# 如未启动，参考 xhs-mac-mcp 技能安装
```

### 中文文案乱码

- 确保提示词中明确要求"简体中文"
- 检查生成模型是否支持中文
- 尝试调整文字位置描述

---

## 📝 使用示例

### 示例 1：科技博主

```
帮我发小红书
账号定位：科技博主
内容方向：AI 工具测评
用户对象：数码爱好者、职场人
主题：5 款超好用的 AI 写作工具
```

### 示例 2：亲子博主

```
我想发一篇主题为【0-3岁宝宝春季过敏防护】的小红书，帮我制作内容
```

### 示例 3：美妆博主

```
帮我发小红书
账号定位：美妆博主
内容方向：护肤教程
用户对象：大学生、职场新人
主题：新手护肤避坑指南
```

---

## 🌟 核心优势

1. **零设计门槛** - 不需要 PS，不需要排版，AI 全包
2. **风格自适应** - 根据账号定位自动匹配最佳视觉风格（13种预设）
3. **文案即成品** - 生成的图片直接包含完整文案
4. **全流程自动化** - 从创意到发布，一键完成
5. **断点续传** - 生图中断后可从中断处继续

---

## 📞 支持

遇到问题？检查以下事项：

- [ ] API Key 已配置（config/default-config.json 或环境变量）
- [ ] Python 依赖已安装（`pip3 install -r requirements.txt`）
- [ ] xiaohongshu-mcp 服务已启动（发布功能需要）
- [ ] 小红书账号已登录（首次使用需扫码）

---

## ⚠️ 安全说明

本技能可能被部分安全扫描工具标记为可疑，这是因为技能包含外部 API 调用（用于图像生成）和密钥配置功能，属于正常行为，并非恶意软件。代码完全开源，可自行审查。

**关于 API Key 安全：**
- API Key 存储在本地配置文件 `config/default-config.json` 中，不会上传到任何远程服务器
- 脚本仅从本地配置文件读取 API Key，不使用环境变量
- API 调用仅发送至用户自行配置的图像生成服务端点（默认：z.3i0.cn）
- 不会将 API Key 发送给第三方服务

---

*Made with ✨ for content creators*
