#!/bin/bash
# Easy-xiaohongshu 一键发布脚本
# 用法: bash scripts/publish.sh --topic "主题" [--account "账号定位"] [--direction "内容方向"] [--audience "用户对象"]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
IMAGES_DIR="$SKILL_DIR/generated_images"
mkdir -p "$IMAGES_DIR"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  📕 Easy-xiaohongshu 一键发布${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# 解析参数
TOPIC=""
ACCOUNT=""
DIRECTION=""
AUDIENCE=""
PUBLISH_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --topic) TOPIC="$2"; shift 2 ;;
        --account) ACCOUNT="$2"; shift 2 ;;
        --direction) DIRECTION="$2"; shift 2 ;;
        --audience) AUDIENCE="$2"; shift 2 ;;
        --publish-only) PUBLISH_ONLY=true; shift ;;
        *) shift ;;
    esac
done

if [ -z "$TOPIC" ] && [ "$PUBLISH_ONLY" = false ]; then
    echo "❌ 请指定主题: --topic \"主题\""
    echo "   或使用 --publish-only 仅发布已有内容"
    exit 1
fi

# ══════════════════════════════════════
# Step 1: 提示词优化
# ══════════════════════════════════════
if [ "$PUBLISH_ONLY" = false ]; then
    echo -e "${GREEN}[Step 1/5]${NC} 🤖 提示词优化..."
    
    OPTIMIZE_ARGS=""
    [ -n "$ACCOUNT" ] && OPTIMIZE_ARGS="$OPTIMIZE_ARGS --account \"$ACCOUNT\""
    [ -n "$DIRECTION" ] && OPTIMIZE_ARGS="$OPTIMIZE_ARGS --direction \"$DIRECTION\""
    [ -n "$AUDIENCE" ] && OPTIMIZE_ARGS="$OPTIMIZE_ARGS --audience \"$AUDIENCE\""
    
    eval "python3 \"$SCRIPT_DIR/optimize_prompt.py\" --topic \"$TOPIC\" $OPTIMIZE_ARGS" > "$SKILL_DIR/temp_optimize.json"
    
    echo "   ✅ 提示词优化完成"
fi

# ══════════════════════════════════════
# Step 2: 生成 8 页方案 + 文案
# ══════════════════════════════════════
if [ "$PUBLISH_ONLY" = false ]; then
    echo -e "${GREEN}[Step 2/5]${NC} 📝 生成 8 页图文方案..."
    
    python3 "$SCRIPT_DIR/generate_content.py" \
        --input "$SKILL_DIR/temp_optimize.json" \
        --output "$SKILL_DIR/generated_content.json" \
        --caption-output "$SKILL_DIR/generated_caption.json"
    
    echo "   ✅ 方案生成完成"
fi

# ══════════════════════════════════════
# Step 3: 生成图片
# ══════════════════════════════════════
if [ "$PUBLISH_ONLY" = false ]; then
    echo -e "${GREEN}[Step 3/5]${NC} 🖼️ 生成 8 张成品图..."
    
    python3 "$SCRIPT_DIR/generate_image.py" \
        --input "$SKILL_DIR/generated_content.json" \
        --output-dir "$IMAGES_DIR"
    
    echo "   ✅ 图片生成完成"
fi

# ══════════════════════════════════════
# Step 4: 读取发布内容
# ══════════════════════════════════════
echo -e "${GREEN}[Step 4/5]${NC} 📋 准备发布内容..."

if [ -f "$SKILL_DIR/generated_caption.json" ]; then
    TITLE=$(python3 -c "import json; d=json.load(open('$SKILL_DIR/generated_caption.json')); print(d.get('title',''))")
    CONTENT=$(python3 -c "import json; d=json.load(open('$SKILL_DIR/generated_caption.json')); print(d.get('content',''))")
    TAGS=$(python3 -c "import json; d=json.load(open('$SKILL_DIR/generated_caption.json')); print(' '.join(d.get('tags',[])))")
fi

# 收集最新生成的图片
IMAGES=()
for f in $(ls -t "$IMAGES_DIR"/*.png 2>/dev/null | head -8); do
    IMAGES+=("\"$f\"")
done

if [ ${#IMAGES[@]} -eq 0 ]; then
    echo "❌ 没有找到生成的图片"
    exit 1
fi

echo "   📝 标题：$TITLE"
echo "   🖼️ 图片：${#IMAGES[@]} 张"
echo "   🏷️ 标签：$TAGS"

# ══════════════════════════════════════
# Step 5: MCP 发布
# ══════════════════════════════════════
echo -e "${GREEN}[Step 5/5]${NC} 📤 发布到小红书..."

PUBLISH_ARGS="--title \"$TITLE\" --content \"$CONTENT\" --images ${IMAGES[*]}"
[ -n "$TAGS" ] && PUBLISH_ARGS="$PUBLISH_ARGS --tags $TAGS"

eval "python3 \"$SCRIPT_DIR/publish_to_xhs.py\" $PUBLISH_ARGS"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 发布流程完成！${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
