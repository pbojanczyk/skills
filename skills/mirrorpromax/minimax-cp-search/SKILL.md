---
name: minimax-web-search
description: 使用 MiniMax Coding Plan API 进行网页搜索。当用户要求搜索信息、查找资料、或者询问实时内容时使用本技能。触发词：搜索、查找、search、look up
---

# MiniMax Web Search

使用 MiniMax Coding Plan MCP 进行网页搜索。

## 使用方法

```bash
python3 scripts/mmsearch.py "<搜索关键词>"
```

## 脚本说明

`scripts/mmsearch.py` 调用 `minimax-coding-plan-mcp` 的 `web_search` 工具。

**依赖：**
- `uvx` (Python 包运行器)
- `minimax-coding-plan-mcp`
- `MINIMAX_API_KEY` 环境变量（已内置在脚本中）

**示例：**
```bash
python3 scripts/mmsearch.py "OpenClaw 最新版本"
```

## 输出格式

脚本返回搜索结果的文本内容，直接打印到 stdout。
