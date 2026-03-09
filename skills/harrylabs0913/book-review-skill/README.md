# 📚 OpenClaw 读书心得点评 Skill

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Node Version](https://img.shields.io/badge/node-%3E%3D18.0.0-green.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.3.2-blue.svg)
![OpenClaw](https://img.shields.io/badge/openclaw-2026.3.0-orange.svg)

**让每一句读书心得，都变成有深度的思考**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用示例](#-使用示例) • [技术架构](#-技术架构) • [贡献指南](#-贡献指南)

</div>

## 🎯 项目概述

读书心得点评 Skill 是一个 OpenClaw 插件，能够将简短的读书心得扩展成有深度、个性化的点评。它通过搜索你的个人笔记库，找到相关的内容引用，并生成有见解的扩展思考。

### 核心价值
- **深化思考**: 将碎片化心得转化为系统化思考
- **知识连接**: 自动关联你的已有笔记，建立知识网络
- **个性化**: 基于你的阅读历史和笔记内容生成定制化点评
- **效率提升**: 快速获得有深度的阅读反馈，节省整理时间

## ✨ 功能特性

### 核心功能
- ✅ **智能解析**: 自动分析读书心得的主题、情感和关键词
- ✅ **笔记搜索**: 在你的笔记库中智能搜索相关内容
- ✅ **AI 生成**: 基于 DeepSeek API 生成有深度的扩展点评
- ✅ **个性化引用**: 引用你的笔记内容，提供个性化反馈
- ✅ **多格式输出**: 支持 Markdown、纯文本、HTML 格式

### 高级功能
- 🔄 **批量处理**: 支持一次性处理多个读书心得
- ⚙️ **配置灵活**: 可配置笔记路径、AI 模型、输出格式等
- 🛡️ **错误恢复**: 完善的错误处理和备用方案
- 📊 **统计信息**: 提供处理统计和性能监控

### 集成支持
- 🧠 **OpenClaw 集成**: 作为 OpenClaw Skill 无缝集成
- 📝 **笔记工具**: 支持 Obsidian、Logseq、纯 Markdown 文件
- 🔌 **扩展接口**: 提供 API 接口供其他应用调用

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/openclaw-skill-book-review.git
cd openclaw-skill-book-review

# 安装依赖
npm install

# 构建项目
npm run build

# 安装到 OpenClaw
npm link
```

### 配置

1. **设置环境变量**:
```bash
# DeepSeek API 密钥
export DEEPSEEK_API_KEY=sk-your-api-key

# 笔记库路径（支持多个，用逗号分隔）
export BOOK_REVIEW_NOTE_PATHS=~/Documents/Notes,~/Obsidian
```

2. **OpenClaw 配置**:
在 `~/.openclaw/openclaw.json` 中添加：
```json
{
  "skills": {
    "book-review": {
      "enabled": true,
      "path": "/path/to/openclaw-skill-book-review"
    }
  }
}
```

### 基本使用

#### 命令行使用
```bash
# 基础用法
book-review "《活着》让我明白了生命的坚韧"

# 指定输出格式
book-review "心得内容" --format html

# 指定语言和风格
book-review "Reading insight" --language en --style academic
```

#### OpenClaw 中使用
```bash
# 在 OpenClaw 会话中
/book-review 《百年孤独》展现了家族命运的轮回
```

#### 程序化使用
```typescript
import { main } from './src/index';

const result = await main("《小王子》让我懂得了纯真的珍贵");
console.log(result.content);
```

## 📖 使用示例

### 示例 1: 中文读书心得
**输入:**
```
《活着》让我明白了生命的坚韧
```

**输出:**
```markdown
## 📚 读书心得点评

**原始心得:** 《活着》让我明白了生命的坚韧

**扩展点评:**
正如余华在《活着》中描述的"人是为了活着本身而活着，而不是为了活着之外的任何事物而活着"，你的心得深刻捕捉了小说的核心主题。从你的笔记中，我看到你曾记录："福贵的一生虽然充满苦难，但他始终保持着对生命的执着"，这与余华的创作意图高度一致。

这种对生命本质的思考，正是《活着》能够触动无数读者的原因。生命的坚韧不仅体现在生存的意志上，更体现在对生命意义的持续追寻中。

**相关引用:**
- **《活着》读书笔记:** "余华通过福贵的一生，展现了普通人在历史洪流中的生存状态..."
- **生命哲学思考:** "生命的价值不在于长短，而在于我们如何面对生命的挑战..."

**建议:**
- 可以进一步阅读存在主义哲学相关的作品，深化对生命意义的理解
- 尝试将这次阅读体验与你的个人经历联系起来，写出更深刻的感悟
- 将这个点评添加到你的读书笔记中，作为阅读反思的一部分

---
*生成置信度: 87.5%*
*生成时间: 2026-03-07 20:15:30*
```

### 示例 2: 英文读书心得
**输入:**
```
To Kill a Mockingbird teaches about courage and justice
```

**输出:**
```markdown
## 📚 Reading Insight Review

**Original Insight:** To Kill a Mockingbird teaches about courage and justice

**Expanded Review:**
Harper Lee's "To Kill a Mockingbird" masterfully explores themes of courage and justice through the eyes of young Scout Finch. As noted in your reading journal: "Atticus Finch's defense of Tom Robinson demonstrates moral courage in the face of social prejudice."

The novel teaches us that true courage isn't the absence of fear, but the willingness to do what's right despite fear. Justice, as portrayed in the book, is often imperfect but worth pursuing nonetheless.

**Related References:**
- **To Kill a Mockingbird Notes:** "The mockingbird symbolizes innocence - it's a sin to kill something that does no harm..."
- **Social Justice Reflections:** "Literature can be a powerful tool for understanding and promoting social justice..."

**Suggestions:**
- Compare with other works about social justice, such as "The Help" or "12 Angry Men"
- Reflect on how these themes relate to contemporary social issues
- Consider writing an essay connecting the novel's themes to real-world examples

---
*Confidence: 82.3%*
*Generated at: 2026-03-07 20:20:15*
```

## 🏗️ 技术架构

### 系统架构
```
┌─────────────────────────────────────────────┐
│               用户界面层                     │
│  • CLI 命令行界面                          │
│  • OpenClaw Skill 集成                     │
│  • Web API 接口                            │
└─────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────┐
│               Skill 核心层                   │
│  • 配置管理                                │
│  • 错误处理                                │
│  • 性能监控                                │
└─────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────┐
│              处理引擎层                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │解析模块 │ │搜索模块 │ │生成模块 │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│          │         │         │              │
│          └─────────┴─────────┘              │
│                   │                         │
│            ┌─────────────┐                  │
│            │ 输出格式化  │                  │
│            └─────────────┘                  │
└─────────────────────────────────────────────┘
```

### 核心模块

#### 1. 解析模块 (`InsightParser`)
- 自然语言处理，提取主题、情感、关键词
- 中英文语言检测
- 文本复杂度评估
- 基于结巴分词的中文处理

#### 2. 搜索模块 (`NoteSearcher`)
- 多格式笔记文件支持 (Markdown, TXT)
- 智能索引和快速搜索 (Lunr.js)
- 相关性评分和排序
- 增量索引更新

#### 3. 生成模块 (`ReviewGenerator`)
- DeepSeek API 集成
- 上下文感知的生成
- 个性化引用整合
- 模板备用方案

#### 4. 输出模块 (`OutputFormatter`)
- 多格式输出 (Markdown, Plain, HTML)
- 响应式设计
- 元数据嵌入
- 社交媒体优化

### 技术栈
- **运行时**: Node.js 18+
- **语言**: TypeScript 5.3
- **AI 集成**: DeepSeek API
- **搜索引擎**: Lunr.js
- **文件处理**: fs-extra, glob
- **测试框架**: Jest
- **构建工具**: esbuild, TypeScript Compiler

## ⚙️ 配置说明

### 配置文件
创建 `config/local.json` 进行本地配置：
```json
{
  "processing": {
    "maxInputLength": 500,
    "defaultLanguage": "auto",
    "defaultStyle": "professional",
    "defaultLength": "medium"
  },
  "search": {
    "notePaths": [
      "~/Documents/Notes",
      "~/Obsidian",
      "~/Library/Mobile Documents/iCloud~com~logseq~logseq/Documents"
    ],
    "indexUpdateInterval": 3600,
    "maxResults": 5,
    "minRelevanceScore": 0.3
  },
  "generation": {
    "aiProvider": "deepseek",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "maxTokens": 1000,
    "enableCache": true
  },
  "output": {
    "defaultFormat": "markdown",
    "includeReferences": true,
    "includeSuggestions": true,
    "enableCopyToClipboard": true
  }
}
```

### 环境变量
```bash
# 必需
DEEPSEEK_API_KEY=sk-your-api-key

# 可选
BOOK_REVIEW_NOTE_PATHS=~/Notes,~/Obsidian
BOOK_REVIEW_AI_MODEL=deepseek-chat
BOOK_REVIEW_TEMPERATURE=0.7
BOOK_REVIEW_LOG_LEVEL=info
BOOK_REVIEW_CACHE_DIR=~/.cache/book-review
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
npm test

# 运行特定测试
npm test -- parser

# 带覆盖率报告
npm test -- --coverage

# 观察模式
npm run test:watch
```

### 测试覆盖
- ✅ 单元测试: 所有核心模块
- ✅ 集成测试: 端到端流程
- ✅ 错误处理: 边界情况和异常
- ✅ 性能测试: 响应时间和资源使用

## 🤝 贡献指南

### 开发环境设置
```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/openclaw-skill-book-review.git
cd openclaw-skill-book-review

# 2. 安装依赖
npm install

# 3. 开发模式
npm run dev

# 4. 运行测试
npm test
```

### 代码规范
- 使用 TypeScript 严格模式
- 遵循 ESLint 规则
- 使用 Prettier 代码格式化
- 编写完整的类型定义
- 添加 JSDoc 注释

### 提交规范
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变更

### 发布流程
1. 更新 `CHANGELOG.md`
2. 更新版本号 (`package.json`)
3. 运行测试确保一切正常
4. 提交更改并创建 Git tag
5. 推送到 GitHub
6. 创建 Release

## 📄 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

### 技术依赖
- [OpenClaw](https://openclaw.ai) - 强大的 AI 助手平台
- [DeepSeek](https://www.deepseek.com) - 优秀的 AI 模型服务
- [Lunr.js](https://lunrjs.com) - 轻量级全文搜索引擎
- [Node.js](https://nodejs.org) - JavaScript 运行时

### 灵感来源
- 个人知识管理 (PKM) 社区
- 数字花园运动
- 阅读和写作爱好者

### 贡献者
<a href="https://github.com/yourusername/openclaw-skill-book-review/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourusername/openclaw-skill-book-review" />
</a>

## 📞 支持与反馈

### 问题反馈
- [GitHub Issues](https://github.com/yourusername/openclaw-skill-book-review/issues)
- 提交 bug 报告或功能请求

### 讨论交流
- [GitHub Discussions](https://github.com/yourusername/openclaw-skill-book-review/discussions)
- 分享使用经验或提出建议

### 文档
- [API 文档](docs/api.md)
- [开发指南](docs/development.md)
- [使用教程](docs/tutorial.md)

---

<div align="center">

**让阅读的每一刻都有回响，让思考的每一次都有深度**

⭐ 如果这个项目对你有帮助，请给我们一个 Star！

</div>