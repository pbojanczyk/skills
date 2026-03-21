#!/usr/bin/env python3
"""
小红书 MCP 自动发布脚本
通过 xiaohongshu-mcp 服务发布图文笔记到小红书

使用方式：
    python3 publish_to_xhs.py --title "标题" --content "正文" --images img1.png img2.png ... --tags tag1 tag2 ...

依赖：
    - xiaohongshu-mcp 服务已启动（默认 http://localhost:18060/mcp）
    - 小红书账号已登录（通过 get_login_qrcode 扫码登录）
"""

import argparse
import json
import sys
import subprocess
import base64
import os

MCP_URL = os.environ.get("XHS_MCP_URL", "http://localhost:18060/mcp")


def mcp_init():
    """初始化 MCP 会话，返回 session_id"""
    result = subprocess.run(
        ["curl", "-s", "-D", "/tmp/xhs_publish_headers",
         "-X", "POST", MCP_URL,
         "-H", "Content-Type: application/json",
         "-d", json.dumps({
             "jsonrpc": "2.0",
             "method": "initialize",
             "params": {
                 "protocolVersion": "2024-11-05",
                 "capabilities": {},
                 "clientInfo": {"name": "easy-xiaohongshu", "version": "1.0"}
             },
             "id": 1
         })],
        capture_output=True, text=True, timeout=15
    )

    # 从响应头提取 session_id
    session_id = None
    with open("/tmp/xhs_publish_headers", "r") as f:
        for line in f:
            if "mcp-session-id" in line.lower():
                session_id = line.strip().split(":", 1)[1].strip()
                break

    if not session_id:
        print("❌ 无法获取 MCP Session ID，请检查 MCP 服务是否运行")
        sys.exit(1)

    # 发送 initialized 通知（不带 id）
    subprocess.run(
        ["curl", "-s", "-X", "POST", MCP_URL,
         "-H", "Content-Type: application/json",
         "-H", f"Mcp-Session-Id: {session_id}",
         "-d", json.dumps({
             "jsonrpc": "2.0",
             "method": "notifications/initialized",
             "params": {}
         })],
        capture_output=True, text=True, timeout=10
    )

    return session_id


def mcp_call(session_id, tool_name, arguments):
    """调用 MCP 工具"""
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", MCP_URL,
         "-H", "Content-Type: application/json",
         "-H", f"Mcp-Session-Id: {session_id}",
         "-d", json.dumps({
             "jsonrpc": "2.0",
             "method": "tools/call",
             "params": {
                 "name": tool_name,
                 "arguments": arguments
             },
             "id": 2
         })],
        capture_output=True, text=True, timeout=120
    )

    try:
        resp = json.loads(result.stdout)
        return resp.get("result", {}).get("content", [])
    except json.JSONDecodeError:
        print(f"❌ MCP 响应解析失败: {result.stdout}")
        return []


def check_login(session_id):
    """检查登录状态"""
    content = mcp_call(session_id, "check_login_status", {})
    for item in content:
        if item.get("type") == "text":
            return "已登录" in item["text"]
    return False


def get_qrcode(session_id):
    """获取登录二维码，保存到文件并打开"""
    content = mcp_call(session_id, "get_login_qrcode", {})

    qr_path = "/tmp/xhs_qr_login.png"
    for item in content:
        if item.get("type") == "image":
            img_data = base64.b64decode(item["data"])
            with open(qr_path, "wb") as f:
                f.write(img_data)
            # 打开二维码图片
            subprocess.run(["open", qr_path], capture_output=True)
            return qr_path
        elif item.get("type") == "text":
            print(item["text"])

    return None


def wait_for_login(session_id):
    """等待用户扫码登录"""
    import time
    print("⏳ 等待扫码登录...")

    for i in range(60):  # 最多等待 5 分钟
        time.sleep(5)
        if check_login(session_id):
            print("✅ 登录成功！")
            return True
        if i % 6 == 5:  # 每 30 秒提示一次
            print(f"   等待中... ({(i+1)*5}s)")

    print("❌ 登录超时（5分钟）")
    return False


def publish(session_id, title, content, images, tags=None):
    """发布图文笔记"""
    args = {
        "title": title,
        "content": content,
        "images": images
    }
    if tags:
        args["tags"] = tags

    print("📤 正在发布笔记，上传图片中...")
    content_resp = mcp_call(session_id, "publish_content", args)

    for item in content_resp:
        if item.get("type") == "text":
            text = item["text"]
            if "发布成功" in text or "发布完成" in text:
                print(f"✅ {text}")
                return True
            elif "失败" in text or "错误" in text:
                print(f"❌ {text}")
                return False
            else:
                print(f"📋 {text}")
                return True

    print("❌ 发布返回异常")
    return False


def main():
    parser = argparse.ArgumentParser(description="小红书 MCP 自动发布")
    parser.add_argument("--title", required=True, help="笔记标题（≤20字）")
    parser.add_argument("--content", required=True, help="笔记正文")
    parser.add_argument("--images", required=True, nargs="+", help="图片路径列表")
    parser.add_argument("--tags", nargs="+", default=[], help="话题标签列表")
    parser.add_argument("--mcp-url", default=None, help="MCP 服务地址")
    parser.add_argument("--json-input", default=None, help="从 JSON 文件读取发布内容")
    parser.add_argument("--json-images", default=None, help="从 JSON 文件读取图片路径列表")
    args = parser.parse_args()

    global MCP_URL
    if args.mcp_url:
        MCP_URL = args.mcp_url

    # 从 JSON 文件读取内容
    title = args.title
    content = args.content
    images = args.images
    tags = args.tags

    if args.json_input:
        with open(args.json_input, "r") as f:
            data = json.load(f)
            title = data.get("title", title)
            content = data.get("content", content)
            tags = data.get("tags", tags or [])

    if args.json_images:
        with open(args.json_images, "r") as f:
            images = json.load(f)

    # 校验
    if len(title) > 20:
        print(f"⚠️ 标题长度 {len(title)} 超过 20 字限制，请缩短")
    if not images:
        print("❌ 至少需要 1 张图片")
        sys.exit(1)

    # 检查图片文件是否存在
    missing = [img for img in images if not os.path.exists(img)]
    if missing:
        print(f"❌ 以下图片文件不存在：")
        for img in missing:
            print(f"   - {img}")
        sys.exit(1)

    print("=" * 50)
    print("📕 小红书自动发布")
    print("=" * 50)
    print(f"📝 标题：{title}")
    print(f"📄 正文：{content[:50]}..." if len(content) > 50 else f"📄 正文：{content}")
    print(f"🖼️ 图片：{len(images)} 张")
    print(f"🏷️ 标签：{', '.join(tags) if tags else '无'}")
    print("=" * 50)

    # Step 1: 初始化 MCP
    print("\n🔗 连接 MCP 服务...")
    session_id = mcp_init()
    print(f"✅ MCP 会话已建立")

    # Step 2: 检查登录状态
    print("\n🔑 检查登录状态...")
    if check_login(session_id):
        print("✅ 已登录")
    else:
        print("❌ 未登录，需要扫码")
        qr_path = get_qrcode(session_id)
        if qr_path:
            print(f"📱 二维码已打开：{qr_path}")
            print("请用小红书 App 扫码登录")
            if not wait_for_login(session_id):
                sys.exit(1)
        else:
            print("❌ 无法获取二维码")
            sys.exit(1)

    # Step 3: 发布
    print()
    success = publish(session_id, title, content, images, tags)

    if success:
        print("\n🎉 发布完成！")
    else:
        print("\n❌ 发布失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
