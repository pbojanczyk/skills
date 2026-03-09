---
name: book-review
description: "将读书心得扩展成有深度的点评，基于用户笔记库提供个性化引用。使用方式：在聊天中输入 /book-review [读书心得]，AI 会基于你的笔记库搜索相关引用，生成有深度的书评。"
metadata:
  {
    "openclaw":
      {
        "emoji": "📚",
        "requires": { "node": ">=18.0.0" },
        "install":
          [
            {
              "id": "npm",
              "kind": "npm",
              "package": "openclaw-skill-book-review",
              "label": "Install book-review skill (npm)",
            },
          ],
      },
  }
---

# Book Review Skill

将读书心得扩展成有深度的点评，基于用户笔记库提供个性化引用。

## 功能特性

- 📖 **读书心得扩展**：将简短的读书笔记扩展成有深度的书评
- 🔍 **智能引用**：基于用户笔记库搜索相关段落进行引用
- 🎯 **个性化推荐**：根据用户阅读历史推荐相关书籍
- 💡 **深度分析**：结合多个知识点进行综合分析

## 使用方式

在聊天中输入：
```
/book-review [你的读书心得]
```

例如：
```
/book-review 今天读到了关于刻意练习的内容很有启发
```

## 技术栈

- TypeScript
- nodejieba (中文分词)
- lunr (全文搜索)
- DeepSeek AI

## 依赖

- Node.js >= 18.0.0
- OpenClaw >= 2026.3.0