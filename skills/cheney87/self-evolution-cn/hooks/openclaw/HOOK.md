---
name: self-evolution-cn
description: "自动识别并记录学习、错误和功能需求，支持多 agent 统计和自动提升"
metadata: {"openclaw":{"emoji":"🧠","events":["agent:bootstrap","message:received","tool:after"]}}
---

# Self-Evolution-CN Hook

自动识别并记录学习、错误和功能需求。

## 功能

### 自动识别

- 用户纠正（"不对"、"错了"等）→ LEARNINGS.md
- 命令失败（非零退出码）→ ERRORS.md
- 知识缺口（用户提供新信息）→ LEARNINGS.md
- 发现更好的方法（"更好的方法"、"优化"等）→ LEARNINGS.md

### 记录格式

详见 `references/format.md`

### 提升规则

- Recurrence-Count >= 3 → 自动提升到 SOUL.md
- Priority = critical → 立即提升
- 多 agent 统计：按 Pattern-Key 累计所有 agent 的 Recurrence-Count

详见 `references/promotion.md`

## 配置

无需配置。启用：
```bash
openclaw hooks enable self-evolution-cn
```

## 多 Agent 支持

所有 agent 共享学习目录，按 `Pattern-Key` 累计 `Recurrence-Count`。

详见 `references/multi-agent.md`

## 环境变量

```bash
export SHARED_LEARNING_DIR="/root/.openclaw/shared-learning"
export AGENT_ID="agent1"
```

## 执行状态和日志

- 状态：`~/.openclaw/skills/self-evolution-cn/heartbeat-state.json`
- 日志：`~/.openclaw/skills/self-evolution-cn/logs/heartbeat-daily.log`

详见 `references/multi-agent.md`
