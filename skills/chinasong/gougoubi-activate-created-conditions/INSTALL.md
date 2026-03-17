# 安装说明

## 从本仓库安装（本地）

从仓库根目录执行（若项目提供安装脚本）：

```bash
# 若有脚本，例如：
# bash scripts/install-gougoubi-activate-created-conditions-skill.sh
```

脚本会将 `skills/gougoubi-activate-created-conditions/SKILL.md` 等复制到目标技能目录（如 `~/.codex/skills/` 或 `.cursor/skills/`）。

## 从 GitHub 安装

若使用 Codex skill installer：

```bash
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo <owner>/<repo> \
  --path skills/gougoubi-activate-created-conditions
```

## 验证

确认技能目录存在且包含 `SKILL.md`：

```bash
ls -la ~/.codex/skills/gougoubi-activate-created-conditions
# 或
ls -la .cursor/skills/gougoubi-activate-created-conditions
```

## 最后一步

重启 Codex/Cursor Agent 运行时以加载新技能。
