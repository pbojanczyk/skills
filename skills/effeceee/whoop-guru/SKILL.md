# Whoop Guru - WHOOP Health Management System

## 简介 / Introduction

Whoop Guru 是一个基于WHOOP手环的智能健康管理系统，为OpenClaw提供完整的健康数据分析、报告生成和AI驱动健康洞察功能。

Whoop Guru is an intelligent health management system based on WHOOP fitness tracker, providing comprehensive health data analysis, report generation, and AI-powered health insights for OpenClaw.

---

## 功能 / Features

### 1. 数据获取 / Data Collection
- WHOOP API 实时数据获取
- 自动刷新最新数据
- 支持: cycles, sleep, recovery, workouts

### 2. 健康分析 / Health Analysis
- 恢复分析 (Recovery Analysis)
- 睡眠分析 (Sleep Analysis)
- 训练分析 (Training Analysis)
- 心率区间分析 (Heart Rate Zone Analysis)
- 睡眠结构分析 (浅睡/深睡/REM)
- 呼吸率追踪
- 睡眠债务计算

### 3. 预测系统 / Prediction System
- 明日恢复预测
- ML加权预测模型
- 趋势预测

### 4. 预警系统 / Alert System
- 恢复过低警告
- 睡眠债务警告
- 过度训练警告

### 5. 健康评分 / Health Score
- 综合健康评分 (0-100)
- 评分维度: 恢复(40%) + 睡眠(30%) + HRV(20%) + 心率(10%)
- 等级: A+/A/A-/B/C/D

### 6. 报告生成 / Report Generation
- 早间简报
- 详细日报
- 完整周报/月报

### 7. 身体电量 / Body Battery
- Body Battery 计算
- 电量等级显示

### 8. AI功能 / AI Features
- AI健康顾问
- 对话式交互
- 个性化建议
- 反馈学习系统

---

## 安装设置 / Setup

### 1. 配置 WHOOP API 凭证

需要从 https://developer.whoop.com 获取 API 凭证。

创建文件 `~/.clawdbot/whoop-credentials.env`:

```bash
WHOOP_CLIENT_ID="your_client_id"
WHOOP_CLIENT_SECRET="your_client_secret"
WHOOP_REFRESH_TOKEN="your_refresh_token"
```

### 2. 环境变量

```bash
export WHOOP_CLIENT_ID="your_client_id"
export WHOOP_CLIENT_SECRET="your_client_secret"
export WHOOP_REFRESH_TOKEN="your_refresh_token"
```

### 3. 安装依赖

```bash
pip install requests pandas matplotlib weasyprint
```

---

## 使用方法 / Usage

### 命令行 / Command Line

```bash
# 进入 skill 目录
cd whoop-guru

# 查看状态
python3 lib/cli.py status

# 生成报告
python3 lib/cli.py report

# 查看评分
python3 lib/cli.py score
```

---

## 核心脚本 / Core Scripts

| 脚本 | 功能 |
|------|------|
| `cli.py` | 主CLI入口 |
| `whoop-fetcher.sh` | WHOOP数据获取 |
| `data_processor.py` | 数据处理 |
| `health_score.py` | 健康评分 |
| `health_advisor.py` | AI健康顾问 |
| `ml_predictor.py` | ML预测 |
| `enhanced_report.py` | 报告生成 |
| `comprehensive_analysis.py` | 综合分析 |
| `feedback_learning.py` | 反馈学习 |
| `notifications.py` | 智能通知 |

---

## 数据存储 / Data Storage

数据存储在 skill 的 `data/` 目录：
- `data/processed/latest.json` - 最新数据
- `data/processed/health_score.json` - 健康评分
- `data/processed/prediction.json` - 预测数据

报告输出到 `reports/` 目录。

---

## 报告模板 / Report Template

完整报告包含13项内容：

1. 核心指标概览
2. 身体电量
3. 恢复分析 + 恢复评分趋势
4. 睡眠分析 + 睡眠详情 + 睡眠结构
5. 训练分析 + 每日活动强度 + 跑步记录 + 心率区间
6. 健康预测
7. 异常预警
8. 模式学习
9. 个性化建议
10. 健康洞察与建议 + 关键指标汇总
11. 行动清单
12. 数据统计
13. 健康评分系统

---

## 依赖 / Dependencies

- Python 3.8+
- curl
- requests
- pandas
- matplotlib
- weasyprint

---

## 授权 / License

Apache License 2.0 - 详见 LICENSE 文件

---

## 版本 / Version

- **v6.0.7** (2026-03-26)

---

## 作者 / Author

HealthGao Team

---

## 仓库 / Repository

https://github.com/effeceee/healthgao
