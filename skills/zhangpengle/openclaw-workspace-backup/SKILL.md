---
name: workspace-backup
description: 自动将 Agent 工作空间备份到 GitHub 仓库。从 openclaw.json 动态读取 agents 配置，每个 agent 对应一个 GitHub 分支。每天 03:00 自动执行。
---

# Workspace Backup

自动备份 OpenClaw 所有 Agent 的工作空间到 GitHub。

## 功能

- 动态读取 `~/.openclaw/openclaw.json` 中的 `agents.list` 配置
- 每个 agent 的工作空间备份到同名 GitHub 分支
- 每个 agent 可自定义工作空间路径（若未指定则使用默认工作空间）
- 每天 03:00 自动执行（通过 OpenClaw cron）

## 使用方式

### 手动执行备份

```bash
~/.openclaw/workspace/skills/workspace-backup/scripts/backup.sh
```

### 查看备份状态

```bash
~/.openclaw/workspace/skills/workspace-backup/scripts/status.sh
```

### 定时任务

已在 OpenClaw cron 中配置，每天 03:00 执行。

## 配置说明

从 `openclaw.json` 读取配置：

```json
{
  "agents": {
    "defaults": {
      "workspace": "/home/ubuntu/.openclaw/workspace"
    },
    "list": [
      {
        "id": "main",
        "workspace": "/home/ubuntu/.openclaw/workspace"
      },
      {
        "id": "formulas",
        "workspace": "/home/ubuntu/.openclaw/workspace-formulas"
      }
    ]
  }
}
```

- `agents.defaults.workspace`: 默认工作空间路径
- `agents.list[].id`: GitHub 分支名称
- `agents.list[].workspace`: 该 agent 的工作空间路径（可选，不指定则使用默认值）

## 脚本说明

| 脚本 | 说明 |
|------|------|
| `backup.sh` | 执行备份（先 git add -A，再检查暂存区，最后 commit → push） |
| `status.sh` | 查看各工作空间的 git 状态 |

## 注意事项

- 确保 SSH Key 已配置好，可以直接 git push
- 首次执行前需要手动 git clone 或在现有目录初始化 git
- 备份失败会记录日志
