---
name: xtoys-app
version: 1.1.0
description: |
  通过 webhook 控制 xtoys.app 设备。
  支持控制各种身体部位的振动强度，用于情趣设备远程控制。
license: MIT
homepage: https://xtoys.app
repository: https://github.com/himeteam/xtoys
metadata:
  author: himeteam
  tags: ["iot", "webhook", "device-control"]
  requirements:
    - python3
    - requests
    - urllib3
---

# Xtoys.app Webhook Skill v1.1.0

通过 webhook API 远程控制 xtoys.app 连接的设备。

## 配置

支持三种配置方式（优先级从高到低）：

### 1. 环境变量（推荐）
```bash
export XTOYS_WEBHOOK_ID="your-webhook-id-here"
```

### 2. 命令行参数
```bash
python3 scripts/xtoys_control.py --webhook-id xxx --action nipples --level 50
```

### 3. 配置文件
在 `config.json` 中设置：
```json
{
  "webhook_id": "your-webhook-id-here"
}
```

获取 webhook ID：
1. 打开 xtoys.app
2. 进入 Settings → Webhook
3. 复制 Webhook ID

## 使用方法

### 命令行

```bash
# 控制特定部位
python3 scripts/xtoys_control.py --action nipples --level 50

# 停止所有设备
python3 scripts/xtoys_control.py --action stop

# 查看支持的部位列表
python3 scripts/xtoys_control.py --list

# 测试连接
python3 scripts/xtoys_control.py --test

# 使用环境变量
XTOYS_WEBHOOK_ID=xxx python3 scripts/xtoys_control.py --action vibrator --level 80

# 显示详细日志
python3 scripts/xtoys_control.py --action nipples --level 30 --verbose
```

### 作为工具调用

```python
from scripts.xtoys_control import XtoysController

# 方式1: 使用上下文管理器（推荐）
with XtoysController("your-webhook-id") as controller:
    controller.send_command("left_nipple", 50)  # 左边乳头 50% 强度
    controller.send_command("clitoris", 80)      # 阴蒂 80% 强度
    controller.stop_all()  # 停止所有

# 方式2: 手动管理
controller = XtoysController("your-webhook-id")
try:
    controller.send_command("both_nipples", 50)
finally:
    controller.close()

# 方式3: 使用环境变量
import os
os.environ["XTOYS_WEBHOOK_ID"] = "your-webhook-id"
with XtoysController() as controller:
    controller.send_command("vagina", 50)

# 批量操作
commands = [
    {"action": "left_nipple", "level": 30},
    {"action": "right_nipple", "level": 30},
    {"action": "clitoris", "level": 50},
]
results = controller.send_batch(commands)
```

## 支持的 Action（身体部位）

> **注意：** xtoys 一次只能操作一个地方。切换部位时会自动将之前的部位设置为 0。

### 身体部位（可单独控制强度）
- `left_nipple` - 左边乳头
- `right_nipple` - 右边乳头
- `both_nipples` - 两边乳头
- `left_breast` - 左边乳房
- `right_breast` - 右边乳房
- `both_breasts` - 两边乳房
- `clitoris` - 阴蒂
- `vagina` - 阴道
- `anus` - 后庭

### 特殊指令
- `stop` - 停止当前正在刺激的部位
- `pause` - 暂停当前正在刺激的部位（同 stop）

## Level（强度）

- 范围：0 - 100
- **0 = 停止该部位**
- 100 = 最大强度

## 工作原理

1. **单部位限制**：xtoys 同时只能刺激一个部位
2. **自动切换**：设置新部位时，会自动将之前的部位设为 0
3. **停止**：使用 `stop` 或将任意部位的 `level` 设为 0

## 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `XTOYS_WEBHOOK_ID` | Webhook ID | `abc123` |
| `XTOYS_LOG_LEVEL` | 日志级别 | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## 示例场景

```bash
# 渐强模式
for i in 10 30 50 70 100; do
  python3 scripts/xtoys_control.py --action nipples --level $i
  sleep 2
done

# 随机波动
python3 scripts/xtoys_control.py --action vibrator --level $((RANDOM % 100))

# 在脚本中使用
export XTOYS_WEBHOOK_ID="your-webhook-id"
python3 scripts/xtoys_control.py --action nipples --level 30
python3 scripts/xtoys_control.py --action vibrator --level 50
python3 scripts/xtoys_control.py --stop
```

## 安全提示

- 始终确保远程控制是经过双方同意的
- 注意使用安全词机制
- 避免长时间高强度使用
- 首次使用建议从低强度开始测试
- webhook ID 视为敏感信息，不要公开分享

## 依赖

```bash
pip install requests urllib3
```

## 更新日志

### v1.1.0
- 修复 `"estim"` 前导空格问题
- 增加环境变量支持 (`XTOYS_WEBHOOK_ID`)
- 改进错误处理和日志系统
- 支持连接池复用和自动重试
- 增加批量操作功能
- 增加连接测试功能
- 支持上下文管理器 (`with` 语句)

### v1.0.0
- 初始版本
- 基本的 webhook 控制功能
