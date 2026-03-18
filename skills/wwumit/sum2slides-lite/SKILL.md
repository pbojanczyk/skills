---
name: sum2slides-lite
description: 对话总结成专业PPT，支持飞书上传
metadata:
  openclaw:
    requires:
      env: ["FEISHU_APP_ID", "FEISHU_APP_SECRET"]
---

# Sum2Slides Lite - 对话总结成PPT

## 🎯 简介

**Sum2Slides Lite** 是一个免费的对话总结成PPT工具，特别适合OpenClaw用户将对话、会议记录、讨论内容快速总结成专业的演示文稿。

## ✨ 核心功能

### 🧠 智能对话分析
- 自动提取关键决策和行动项
- 识别重要要点和问题
- 智能生成标题和结构

### 🎨 专业PPT生成
- 支持 **PowerPoint** 和 **WPS Office**
- 多种专业模板 (商务/技术/教育)
- 标准 .pptx 格式，兼容性好

### ☁️ 飞书平台集成
- 自动上传到飞书云盘
- 生成文件分享链接
- 团队协作支持

### 🔒 权限友好设计
- **优雅降级方案**: 无权限也能生成文件
- 自动检测系统权限
- 清晰的权限说明

## 🚀 快速开始

### 🎯 版本说明: v1.1.2

**标准安装方式**: 本版本采用ClawHub Skills标准安装方式，无需复杂的安装脚本。

### 📋 安装前必读
请选择适合你的安装方式:

#### **方式A: 手动复制 (最安全，推荐)**
```bash
# 1. 解压后手动复制文件
unzip sum2slides-lite-v1.2.0-noflag.zip
cd sum2slides-lite-v1.2.0-noflag
cp -r * ~/.openclaw/skills/sum2slides-lite/
```

#### **方式B: 符号链接 (开发者友好)**
```bash
# 保持源文件位置，创建符号链接
ln -s /path/to/sum2slides-lite-v1.2.0-noflag ~/.openclaw/skills/sum2slides-lite
```

#### **方式C: pip安装 (标准Python包)**
```bash
cd sum2slides-lite-v1.2.0-noflag
pip install -e .  # 可编辑安装
```

### 🔒 安全验证 (安装前建议)
```bash
# 1. 检查所有代码
find . -name "*.py" -exec head -20 {} \;

# 2. 验证无隐藏操作
grep -r "subprocess\|os.system\|eval\|exec\|download" . --include="*.py"

# 3. 运行安全验证
python INSTALL_VERIFICATION.py
```

### ⚙️ 环境配置 (可选)
```bash
# 仅当使用飞书上传时需要
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"

# 安装Python依赖 (仅当需要PPT生成时)
pip install python-pptx>=0.6.21
```

### ✅ 验证安装
```bash
# 运行权限检查
python quick_permission_check.py

# 运行功能测试
python simple_sum2slides_test.py
```

### 📚 详细安装指南
请参阅: [INSTALL_WITHOUT_SETUP.md](INSTALL_WITHOUT_SETUP.md) - 无脚本安装详细指南

其他重要文档:
- [SECURE_INSTALLATION_GUIDE.md](SECURE_INSTALLATION_GUIDE.md) - 安全使用指南
- [INSTALL_VERIFICATION.py](INSTALL_VERIFICATION.py) - 安装验证脚本
- [docs/SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md) - 完整安全指南

### 基本使用
```python
from sum2slides import sum2slides

# 将对话总结成PPT
result = sum2slides(
    conversation_text="你的对话内容...",
    title="会议总结",
    software="powerpoint"  # 或 "wps"
)

if result['success']:
    print(f"PPT已生成: {result['ppt_info']['file_path']}")
```

## 🔧 详细配置

### 配置文件
编辑 `config/config.yaml`:
```yaml
basic:
  output_dir: "~/Desktop/Sum2Slides"
  default_software: "powerpoint"
  default_template: "business"

feishu:
  enabled: false
  app_id: ""
  app_secret: ""
```

### 环境变量
复制 `.env.example` 为 `.env` 并填写:
```bash
FEISHU_APP_ID=your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here
OUTPUT_DIR=~/Desktop/Sum2Slides
```

## 📊 使用场景

### 1. 会议总结
```
会议讨论 → 自动分析 → PPT报告
```

### 2. 学习笔记整理
```
学习内容 → 要点提取 → 教学PPT
```

### 3. 项目汇报
```
项目进展 → 数据整理 → 汇报PPT
```

## 🛠️ 技术架构

### 模块化设计
```
sum2slides-lite/
├── core/          # 核心功能 (可复用)
│   ├── base_generator.py
│   ├── pptx_generator.py
│   ├── wps_generator.py
│   └── content_planner.py
├── platforms/     # 平台集成 (可扩展)
│   ├── base_platform.py
│   └── feishu/feishu_platform.py
├── config/       # 配置管理
├── utils/        # 工具函数
└── examples/     # 使用示例
```

### 兼容性
- **操作系统**: macOS, Windows, Linux
- **Python**: 3.7+
- **PPT软件**: PowerPoint 2010+, WPS Office 10+
- **平台**: 飞书

## 🔒 权限说明与操作风险

### 必需权限
1. **文件系统**: 写入桌面目录的权限
2. **网络**: 访问飞书API的权限

### 可选权限 (macOS)
- AppleScript自动化权限 (增强功能)
- 系统偏好设置 → 安全性与隐私 → 隐私 → 自动化

### 优雅降级方案
**核心优势: 用户永远能得到可用的PPT文件**

| 权限状态 | PPT生成能力 | 结果 |
|---------|------------|------|
| **完全授权** | ✅ 全自动化 | 功能完整，体验最佳 |
| **无AppleScript** | ✅ 标准生成 | 生成标准 .pptx，两种软件都能打开 |
| **无网络权限** | ✅ 本地保存 | 文件保存在桌面，可手动分享 |
| **无文件权限** | ⚠️ 提示更改目录 | 用户选择有权限的目录 |

## ⚠️ 操作风险与不一致性说明

### 平台功能不一致
- **AppleScript自动化**: 仅支持macOS系统
- **PowerPoint集成**: 需要软件安装
- **跨平台支持**: 功能在不同平台有差异

### 配置行为不一致
- **默认软件无安装**: 自动降级到WPS Office
- **模板文件缺失**: 使用内置基本模板
- **输出目录问题**: 提示用户选择目录

### 详细风险说明
请查看 `docs/OPERATIONAL_RISKS.md` 了解完整的操作风险和缓解措施。

## 📁 文件清单

### 核心文件
```
📄 sum2slides.py                 # 主程序
📄 __init__.py                  # 包初始化
📄 quick_permission_check.py    # 权限检测
📄 simple_sum2slides_test.py    # 功能测试
📄 setup_info.py                # 安装信息文件
📄 SKILL.md                     # 本文档
```

### 文档文件
```
📄 docs/PERMISSIONS.md          # 权限说明
📄 docs/USER_GUIDE.md           # 用户指南
📄 README.md                    # 项目说明
📄 .env.example                 # 环境变量示例
📄 clawhub.json                 # Claw Hub配置
```

## 🔧 工具函数

### 权限检测
```bash
# 检查系统权限
python quick_permission_check.py
```

### 功能测试
```bash
# 测试核心功能
python simple_sum2slides_test.py
```

### 使用示例
```bash
# 运行示例
python examples/basic_usage.py
```

## 🤝 支持与贡献

### 问题反馈
- **GitHub Issues**: 问题报告和功能建议
- **Discord社区**: 实时支持和讨论

### 文档资源
- **使用指南**: `docs/USER_GUIDE.md`
- **权限说明**: `docs/PERMISSIONS.md`
- **API文档**: 查看代码注释

### 开源社区
- **许可证**: MIT License
- **贡献**: 欢迎提交PR和功能建议
- **反馈**: 收集用户使用体验

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**Sum2Slides Lite** - 让对话总结变得简单高效！ 🚀

## 🔄 更新日志

### 版本 1.0.0 (2026-03-18)
- 初始版本发布
- 核心对话分析功能
- PPT生成支持 (PowerPoint/WPS)
- 飞书平台集成
- 权限检测系统
- 完整文档和示例

---

**开始使用 Sum2Slides Lite，提升你的工作效率！**