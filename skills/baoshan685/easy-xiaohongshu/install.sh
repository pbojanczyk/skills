#!/bin/bash
# Easy-xiaohongshu 安装脚本

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "✨ Easy-xiaohongshu - 小红书 AI 图文自动发布"
echo ""

# 检查 Python
echo "【1/2】检查 Python 环境..."
if command -v python3 &> /dev/null; then
    echo "  ✅ $(python3 --version)"
else
    echo "  ❌ 未检测到 Python3，请先安装"
    exit 1
fi

# 安装依赖
echo "【2/2】安装 Python 依赖..."
pip3 install -r "$SKILL_DIR/requirements.txt" --quiet 2>/dev/null
echo "  ✅ 依赖安装完成"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║  ✅ 安装完成！                         ║"
echo "╠════════════════════════════════════════╣"
echo "║                                        ║"
echo "║  下一步：配置 API Key                   ║"
echo "║  编辑 config/default-config.json        ║"
echo "║  填写 api.api_key 字段                  ║"
echo "║                                        ║"
echo "║  如需自动发布：启动 xiaohongshu-mcp     ║"
echo "║  服务（参考 xhs-mac-mcp 技能）          ║"
echo "╚════════════════════════════════════════╝"
