#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像生成脚本 - 调用 Gemini API 生成小红书成品图
优化版：从配置文件读取 API key，生一张发一张
"""

import os
import sys
import json
import time
import base64
import signal
import requests
from datetime import datetime

# 获取配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(SKILL_DIR, 'config', 'default-config.json')

# 进度文件（支持断点续传）
PROGRESS_FILE = os.path.join(SKILL_DIR, 'generated_images', '.progress.json')


def load_config():
    """加载配置文件"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_progress(page_num, output_path):
    """保存进度"""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    progress = load_progress()
    progress[str(page_num)] = output_path
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def load_progress():
    """加载进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {}


def clear_progress():
    """清除进度"""
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)


def generate_image(prompt, output_path, config):
    """
    调用 Gemini API 生成单张图片
    """
    api_key = config['api'].get('api_key', '')
    base_url = config['api']['base_url']
    model = config['api']['model']
    timeout = config['api']['timeout_seconds']
    max_retries = config['api']['max_retries']

    if not api_key:
        print("❌ 错误：未配置 API Key。请在 config/default-config.json 中配置 api.api_key", flush=True)
        return False

    url = f"{base_url}/models/{model}:generateContent"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
        }
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)

            if response.status_code == 200:
                result = response.json()

                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        for part in candidate['content']['parts']:
                            # inlineData 格式
                            if 'inlineData' in part:
                                image_data = part['inlineData']
                                if image_data.get('mimeType', '').startswith('image/'):
                                    image_bytes = base64.b64decode(image_data['data'])
                                    with open(output_path, 'wb') as f:
                                        f.write(image_bytes)
                                    return True

                            # Markdown 格式
                            if 'text' in part:
                                text = part['text']
                                import re
                                markdown_pattern = r'!\[image\]\(data:image/(jpeg|png|jpg);base64,([A-Za-z0-9+/=]+)\)'
                                match = re.search(markdown_pattern, text)
                                if match:
                                    image_bytes = base64.b64decode(match.group(2))
                                    with open(output_path, 'wb') as f:
                                        f.write(image_bytes)
                                    return True

                print(f"⚠️  API 返回格式异常", flush=True)
                return False

            elif response.status_code == 429:
                print(f"⚠️  速率限制，等待 60 秒...", flush=True)
                time.sleep(60)
                continue
            else:
                print(f"❌ API 错误：{response.status_code}", flush=True)
                if response.status_code >= 500:
                    time.sleep(10)
                    continue
                return False

        except requests.exceptions.Timeout:
            print(f"⚠️  请求超时，重试...", flush=True)
            time.sleep(10)
            continue
        except Exception as e:
            print(f"❌ 错误：{e}", flush=True)
            return False

    print("❌ 超过最大重试次数", flush=True)
    return False


def generate_all(pages, output_dir, config, callback=None):
    """
    生成所有页面的图片，支持断点续传
    callback(page_num, total, status, path) - 每张图片完成时回调
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    page_names = {
        1: 'cover', 2: 'page2', 3: 'page3', 4: 'page4',
        5: 'page5', 6: 'page6', 7: 'page7', 8: 'ending'
    }

    # 检查已有进度
    progress = load_progress()
    completed = []
    image_paths = []

    # 如果有之前的进度，复用时间戳
    if progress:
        # 取已有的时间戳
        first_path = list(progress.values())[0]
        old_ts = os.path.basename(first_path).split('_')[0] + '_' + os.path.basename(first_path).split('_')[1]
        timestamp = old_ts

    for i, page in enumerate(pages, 1):
        page_name = page_names.get(i, f'page{i}')
        filename = f"{timestamp}_{page_name}.png"
        output_path = os.path.join(output_dir, filename)

        # 断点续传：已完成的跳过
        if str(i) in progress and os.path.exists(progress[str(i)]):
            print(f"⏭️  第 {i} 页已完成，跳过", flush=True)
            image_paths.append(progress[str(i)])
            completed.append(i)
            if callback:
                callback(i, len(pages), 'skipped', progress[str(i)])
            continue

        prompt = page.get('成品图生成提示词', '')
        if not prompt:
            print(f"⚠️  第 {i} 页缺少提示词，跳过", flush=True)
            continue

        print(f"📸 第 {i}/{len(pages)} 页 生成中...", flush=True)

        if generate_image(prompt, output_path, config):
            save_progress(i, output_path)
            image_paths.append(output_path)
            completed.append(i)
            print(f"✅ 第 {i}/{len(pages)} 页完成：{filename}", flush=True)
            if callback:
                callback(i, len(pages), 'success', output_path)
        else:
            print(f"❌ 第 {i}/{len(pages)} 页失败", flush=True)
            if callback:
                callback(i, len(pages), 'failed', None)

        # 间隔避免速率限制
        if i < len(pages):
            time.sleep(3)

    # 全部完成后清除进度
    if len(completed) == len(pages):
        clear_progress()

    return image_paths


def main():
    config = load_config()
    api_key = config['api'].get('api_key', '')
    base_url = config['api']['base_url']
    model = config['api']['model']

    # 从 stdin 读取 JSON 方案
    input_data = sys.stdin.read()
    pages = json.loads(input_data)

    if not isinstance(pages, list) or len(pages) != 8:
        print(f"❌ 需要 8 页方案，当前 {len(pages) if isinstance(pages, list) else 0} 页")
        sys.exit(1)

    output_dir = os.path.join(SKILL_DIR, 'generated_images')
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    print(f"🎯 开始生成 {len(pages)} 张图片", flush=True)
    print(f"📁 输出目录：{output_dir}", flush=True)

    # 回调：每生成一张输出 JSON 进度
    def on_progress(page, total, status, path):
        result = {"page": page, "total": total, "status": status}
        if path:
            result["path"] = path
        print(f"__PROGRESS__{json.dumps(result, ensure_ascii=False)}", flush=True)

    image_paths = generate_all(pages, output_dir, config, callback=on_progress)

    print(f"\n🎉 生成完成：{len(image_paths)}/{len(pages)} 张", flush=True)
    if image_paths:
        print(json.dumps(image_paths, ensure_ascii=False))


if __name__ == '__main__':
    main()
