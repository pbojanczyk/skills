---
name: openclaw-soul
description: OpenClaw 自我进化框架一键部署。安装宪法(AGENTS.md)、可进化灵魂(SOUL.md)、心跳系统、六层记忆架构、目标管理、思维方法论（HDD/SDD）、跨会话存档（save-game/load-game），并通过场景化对话引导用户定义 Agent 性格。自动配置 EvoClaw（审批制进化）和 Self-Improving Agent（自主学习）。触发场景：(1) 用户说"灵魂框架"、"部署灵魂"、"部署灵魂系统" (2) 用户说"BOOTSTRAP"、"首次对话"、"第一次对话" (3) 用户说"安装进化框架"、"部署进化框架" (4) 用户提到"openclaw-soul"。注意：这是 OpenClaw 部署的第一步，完成后会引导使用 openclaw-setup 配置技术参数。
metadata:
  clawdbot:
    emoji: "🧬"
    requires:
      bins: []
    os: ["linux", "darwin", "win32"]
---

# openclaw-soul — Self-Evolution Framework

为 OpenClaw 安装完整的自我进化框架：宪法 + 可进化灵魂 + 结构化心跳协议 + 六层记忆 + 思维方法论 + 跨会话存档 + 目标管理 + 治理配置。

**安装内容**：
- 9 个工作区文件（AGENTS.md, SOUL.md, HEARTBEAT.md, BOOTSTRAP.md, USER.md, IDENTITY.md, GOALS.md, working-memory.md, long-term-memory.md）
- 7 个依赖 skill（evoclaw, self-improving, hdd, sdd, save-game, load-game, project-skill-pairing）
- 2 个记忆基础设施脚本（merge-daily-transcript.js, auto-commit.sh）
- Heartbeat 定时任务配置
- EvoClaw 治理配置（advisory 模式 + soul-revisions 回滚）
- 六层记忆目录结构 + Git 版本管理
- 向量搜索配置引导
- 引导对话启动（BOOTSTRAP.md）

---

## §1 [GATE] 环境检测

**在执行任何操作之前，必须先完成此步骤。跳过此步骤是禁止的。**

### 1a. 自动检测工作区

自动检测 `~/.openclaw/workspace/` 是否存在：

```bash
WORKSPACE="$HOME/.openclaw/workspace"
test -d "$WORKSPACE" && echo "WORKSPACE=$WORKSPACE — OK" || echo "FAIL: $WORKSPACE not found"
```

- **存在** → 设置 `$WORKSPACE`，无需任何用户交互，直接继续
- **不存在** → 报错并停止：

> "工作区 `~/.openclaw/workspace/` 不存在。请先确认 OpenClaw 已正确安装，或手动创建该目录后重新触发。"

### 1b. 环境检查

1. **openclaw.json 可读**：检查 `$WORKSPACE/../openclaw.json` 是否存在且为有效 JSON
2. **clawhub CLI 可用**：`which clawhub` 或检查 `~/.openclaw/bin/clawhub` 或 `/usr/local/bin/clawhub` 或 `/usr/bin/clawhub`
3. **列出已有文件**：检查以下 9 个文件是否已存在于 `$WORKSPACE`：
   - AGENTS.md, SOUL.md, HEARTBEAT.md, BOOTSTRAP.md, GOALS.md
   - USER.md, IDENTITY.md, working-memory.md, long-term-memory.md

**判断逻辑**：
- openclaw.json 不存在或无效 → **停止**，告知用户修复
- clawhub 不可用 → 记录为 warn，继续（§3 会使用 fallback）
- 已有文件 → 标记需要备份，继续

**如果 clawhub 不可用**，告知用户：

> "未检测到 clawhub（OpenClaw 技能包管理器）。将使用离线 fallback 或内联版本安装依赖 skill，功能完整，只是管理方式不同。如需安装 clawhub：`npm install -g clawhub`"

### 1c. 开场状态提示

环境检查通过后，输出：

> "我正在帮你做初始化部署，需要装一些核心文件和配置，大概几分钟的时间。你先等我一下，完成了我会通知你。
>
> 部署完之后，我们就开始认识彼此。"

---

## §2 [REQUIRED] 部署文件

**使用 bash cp 部署所有文件。禁止使用 Write/Edit 工具写入模板内容——大文件容易被截断或出错。`cp` 是操作系统级字节复制，100% 可靠。**

### 2a. 获取 skill 目录路径

```bash
# 获取本 skill 的安装路径
SKILL_DIR="$WORKSPACE/skills/openclaw-soul"
# 如果 skill 不在 workspace/skills/ 下，尝试其他常见路径
test -d "$SKILL_DIR" || SKILL_DIR="$(find ~/.openclaw -path '*/openclaw-soul/references' -type d 2>/dev/null | head -1 | sed 's|/references$||')"
echo "SKILL_DIR=$SKILL_DIR"
```

确认 `$SKILL_DIR/references/` 目录存在且包含模板文件。如果找不到，报错停止。

### 2b. 备份已有文件 + 复制模板

```bash
# 备份已有文件
for file in AGENTS.md SOUL.md HEARTBEAT.md BOOTSTRAP.md USER.md IDENTITY.md GOALS.md working-memory.md long-term-memory.md; do
  [ -f "$WORKSPACE/$file" ] && cp "$WORKSPACE/$file" "$WORKSPACE/$file.backup.$(date +%Y%m%d-%H%M%S)"
done

# 复制 9 个模板文件
cp "$SKILL_DIR/references/agents-template.md" "$WORKSPACE/AGENTS.md"
cp "$SKILL_DIR/references/soul-template.md" "$WORKSPACE/SOUL.md"
cp "$SKILL_DIR/references/heartbeat-template.md" "$WORKSPACE/HEARTBEAT.md"
cp "$SKILL_DIR/references/bootstrap-guide.md" "$WORKSPACE/BOOTSTRAP.md"
cp "$SKILL_DIR/references/user-template.md" "$WORKSPACE/USER.md"
cp "$SKILL_DIR/references/identity-template.md" "$WORKSPACE/IDENTITY.md"
cp "$SKILL_DIR/references/goals-template.md" "$WORKSPACE/GOALS.md"
cp "$SKILL_DIR/references/working-memory-template.md" "$WORKSPACE/working-memory.md"
cp "$SKILL_DIR/references/long-term-memory-template.md" "$WORKSPACE/long-term-memory.md"
```

### 2c. 创建目录结构 + 部署脚本

```bash
# 创建六层记忆目录 + EvoClaw 目录 + 脚本目录 + soul-revisions
mkdir -p "$WORKSPACE/memory/"{daily,entities,transcripts,projects,voice,experiences,significant,reflections,proposals,pipeline}
mkdir -p "$WORKSPACE/scripts"
mkdir -p "$WORKSPACE/soul-revisions"

# 复制记忆基础设施脚本
cp "$SKILL_DIR/fallback/memory-deposit/scripts/merge-daily-transcript.js" "$WORKSPACE/scripts/"
cp "$SKILL_DIR/fallback/memory-deposit/scripts/auto-commit.sh" "$WORKSPACE/scripts/"
chmod +x "$WORKSPACE/scripts/auto-commit.sh"
```

### 2d. 验证部署

```bash
# 验证所有文件非空
for file in AGENTS.md SOUL.md HEARTBEAT.md BOOTSTRAP.md USER.md IDENTITY.md GOALS.md working-memory.md long-term-memory.md; do
  test -s "$WORKSPACE/$file" && echo "OK: $file" || echo "FAIL: $file is empty or missing"
done
```

如果任何文件验证失败，立即停止并报告错误。

---

## §3 [REQUIRED] 依赖 Skill 安装（三级 Fallback）

### 3a. 检查 clawhub 可用性

```bash
which clawhub || test -f ~/.openclaw/bin/clawhub
CLAWHUB_AVAILABLE=$?
```

### 3b. 安装 EvoClaw

检查 `$WORKSPACE/skills/evoclaw/SKILL.md` 是否存在：

**已安装** → 跳过，告知用户

**未安装** → 按优先级尝试：

1. **Level 1 - clawhub 安装**（如果可用）
   ```bash
   clawhub install evoclaw --force
   ```

2. **Level 2 - 离线 Fallback**（如果 Level 1 失败或 clawhub 不可用）
   ```bash
   cp -r "$SKILL_DIR/fallback/evoclaw" "$WORKSPACE/skills/"
   ```

3. **Level 3 - AGENTS.md 内联版本**
   > "使用 AGENTS.md 内联版本。核心功能完整（Identity 变更需批准、用户纠正自动学习、SOUL.md 变更前自动快照）。与完整版的区别：内联版规则写在 AGENTS.md，完整版是独立 skill 可通过 clawhub 更新。"

### 3c. 安装 Self-Improving Agent

检查 `$WORKSPACE/skills/self-improving/SKILL.md` 是否存在：

**已安装** → 跳过，告知用户

**未安装** → 按优先级尝试：

1. **Level 1 - clawhub 安装**（如果可用）
   ```bash
   clawhub install self-improving --force
   ```

2. **Level 2 - 离线 Fallback**（如果 Level 1 失败或 clawhub 不可用）
   ```bash
   cp -r "$SKILL_DIR/fallback/self-improving" "$WORKSPACE/skills/"
   ```

3. **Level 3 - AGENTS.md 内联版本**
   > "使用 AGENTS.md 内联版本。核心功能完整（用户纠正自动学习、规则持久化、30天未使用自动归档）。"

### 3d. 安装思维方法论与项目管理 Skills

以下 5 个 skill 使用同样的三级 Fallback 机制安装：

| Skill | clawhub 名称 | Fallback 路径 | 功能 |
|-------|-------------|-------------|------|
| HDD | `hdd` | `fallback/hdd/` | 假设驱动开发 |
| SDD | `sdd` | `fallback/sdd/` | 场景驱动开发 |
| save-game | `save-game` | `fallback/save-game/` | 项目存档 |
| load-game | `load-game` | `fallback/load-game/` | 项目恢复 |
| project-skill-pairing | `project-skill-pairing` | `fallback/project-skill-pairing/` | 项目与 Skill 结对 |

对每个 skill，按顺序尝试：
1. **Level 1**: `clawhub install <name> --force`（如果可用）
2. **Level 2**: `cp -r "$SKILL_DIR/fallback/<name>" "$WORKSPACE/skills/"`
3. **Level 3**: 记录警告，继续下一个

### 3e. 验证结果

安装完成后，逐项报告：

```
✓ EvoClaw: [installed from clawhub | installed from fallback | using inline version]
✓ Self-Improving: [installed from clawhub | installed from fallback | using inline version]
✓ HDD: [installed from clawhub | installed from fallback | ⚠️ not installed]
✓ SDD: [installed from clawhub | installed from fallback | ⚠️ not installed]
✓ save-game: [installed from clawhub | installed from fallback | ⚠️ not installed]
✓ load-game: [installed from clawhub | installed from fallback | ⚠️ not installed]
✓ project-skill-pairing: [installed from clawhub | installed from fallback | ⚠️ not installed]
```

---

## §4 [REQUIRED] 配置系统

### 4a. EvoClaw 治理配置

写入 `$WORKSPACE/memory/evoclaw-state.json`：

```json
{
  "mode": "advisory",
  "require_approval": ["Core Identity", "Capability Tree", "Value Function"],
  "auto_sections": ["Working Style", "User Understanding", "Evolution Log"],
  "revision_dir": "soul-revisions",
  "initialized": true
}
```

验证 JSON 可解析。

### 4b. Self-Improving Agent 初始化

确保目录和文件存在：

```bash
mkdir -p ~/self-improving/{projects,domains,archive}
```

如果以下文件**不存在**，创建初始版本（已存在则不覆盖）：

**~/self-improving/memory.md**:
```markdown
# Self-Improving Memory

> Execution patterns and learned rules. Updated after corrections and lessons.

(empty — will accumulate through use)
```

**~/self-improving/corrections.md**:
```markdown
# Corrections Log

> Failed attempts and their fixes. Each entry prevents the same mistake twice.

(empty — will accumulate through use)
```

**~/self-improving/index.md**:
```markdown
# Self-Improving Index

> Quick reference to all domains, projects, and archived knowledge.

## Domains
(none yet)

## Projects
(none yet)

## Archive
(none yet)
```

### 4c. Heartbeat 配置

使用 `openclaw config set` 更新 heartbeat 设置：

```bash
openclaw config set agents.defaults.heartbeat.every "1h"
openclaw config set agents.defaults.heartbeat.target "last"
openclaw config set agents.defaults.heartbeat.directPolicy "allow"
```

如果 `openclaw config set` 不可用，直接编辑 `openclaw.json`，确保 `agents.defaults.heartbeat` 包含 `every: "1h"`, `target: "last"`, `directPolicy: "allow"`。

### 4d. 向量搜索配置

**没有向量搜索的记忆系统是摆设。此步骤不可跳过。**

1. 执行 `memory_search(query="test memory recall")` 检测当前状态
2. **有结果** → embedding 已就绪，跳到配置 extraPaths
3. **报错或无结果** → 需要配置 embedding provider

向用户说明并推荐方案：

> "向量搜索需要一个 embedding API key，这是记忆系统的核心能力。"

| 方案 | 模型 | 价格 | 说明 |
|------|------|------|------|
| **Gemini** | `gemini-embedding-001` | 免费额度大 | 配置最简单 |
| **硅基流动 SiliconFlow** | `BAAI/bge-large-zh-v1.5` 或 `BAAI/bge-m3` | 免费（注册送额度） | 中文效果好，OpenAI 兼容接口 |
| **OpenAI** | `text-embedding-3-small` | 付费 | 效果稳定 |

硅基流动配置示例（provider 设为 openai，用自定义 baseUrl）：
```json5
memorySearch: {
  provider: "openai",
  model: "BAAI/bge-large-zh-v1.5",
  remote: {
    baseUrl: "https://api.siliconflow.cn/v1",
    apiKey: "<用户的 SiliconFlow API Key>"
  }
}
```

确认用户选定方案后，用 `gateway(action=config.patch)` 或直接编辑 `openclaw.json` 配好。

配置 extraPaths：
```json5
memorySearch: {
  extraPaths: ["memory/transcripts", "memory/projects", "AGENTS.md"]
}
```

开启高级搜索功能：
```json5
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "query": {
          "hybrid": {
            "mmr": { "enabled": true, "lambda": 0.7 },
            "temporalDecay": { "enabled": true, "halfLifeDays": 30 }
          }
        },
        "cache": { "enabled": true, "maxEntries": 50000 }
      }
    }
  }
}
```

验证：再次执行 `memory_search(query="test")` 确认可用。如果 memory/ 下还没有文件，告知用户："向量搜索已就绪，等积累了笔记后就能搜到了。"

### 4e. Git 版本管理初始化

检查 `$WORKSPACE/.git/` 是否存在：

**不存在** →
```bash
cd $WORKSPACE && git init
```

写入 `.gitignore`（排除敏感文件和临时文件）：
```
.env*
*.secrets
credentials.json
tmp/
node_modules/
.DS_Store
```

执行首次提交：
```bash
git add -A && git commit -m "init: openclaw-soul workspace"
```

**已存在** → 检查 `.gitignore` 包含上述排除项，缺的补上。

---

## §5 [FINAL] 验证 + 启动

### 5a. 核心验证清单（10 项）

逐项检查并报告 pass/fail：

| # | 检查项 | 验证方法 |
|---|--------|---------|
| 1 | AGENTS.md 非空 | `test -s $WORKSPACE/AGENTS.md` |
| 2 | SOUL.md 非空 | `test -s $WORKSPACE/SOUL.md` |
| 3 | BOOTSTRAP.md 非空 | `test -s $WORKSPACE/BOOTSTRAP.md` |
| 4 | USER.md 非空 | `test -s $WORKSPACE/USER.md` |
| 5 | IDENTITY.md 非空 | `test -s $WORKSPACE/IDENTITY.md` |
| 6 | EvoClaw 已安装 | `test -f $WORKSPACE/skills/evoclaw/SKILL.md` 或确认使用内联版本 |
| 7 | Self-Improving 已安装 | `test -f $WORKSPACE/skills/self-improving/SKILL.md` 或确认使用内联版本 |
| 8 | evoclaw-state.json 有效 | 读取并验证 `mode=advisory` |
| 9 | Heartbeat 配置已写入 | 读取 openclaw.json 确认 heartbeat 字段 |
| 10 | Git 已初始化 | `test -d $WORKSPACE/.git` |

**输出格式**：

```
✓ AGENTS.md — pass
✓ SOUL.md — pass
✓ BOOTSTRAP.md — pass
✓ USER.md — pass
✓ IDENTITY.md — pass
✓ EvoClaw — pass (installed from fallback)
✓ Self-Improving — pass (installed from fallback)
✓ evoclaw-state.json — pass
✓ Heartbeat — pass
✓ Git — pass
```

**判断**：
- 全部 pass → 继续触发 BOOTSTRAP
- 任何 fail → 列出失败项，提示用户手动修复

### 5b. 触发引导对话

**只有 5a 全部通过后才执行。**

1. 读取 `$WORKSPACE/BOOTSTRAP.md`
2. 告知用户：

> "部署完成了！
>
> 已安装：宪法、可进化灵魂、心跳协议、六层记忆、思维方法论、跨会话存档、目标管理、EvoClaw 治理、Self-Improving Agent。
>
> 接下来我们聊一聊，分三步：
> 1. **认识你** — 了解你是谁，在做什么，需要什么帮助
> 2. **定义我的性格** — 通过场景问答，选择我的沟通风格
> 3. **确认身份** — 给我起个名字
>
> 这次对话会塑造我的灵魂（SOUL.md），之后我就能按你的方式工作了。"

3. **立即开始执行 BOOTSTRAP.md 的 Phase 1**
4. 此 skill 的使命到此结束。后续由 BOOTSTRAP.md + AGENTS.md + SOUL.md 接管运行

---

_openclaw-soul v2.1.0 — Reliable bash cp deployment, streamlined 5-step flow. Give your AI a soul that grows._
