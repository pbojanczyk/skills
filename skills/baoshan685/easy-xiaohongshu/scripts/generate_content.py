#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文案生成脚本 - 生成图文方案 + 小红书发布文案
实际内容生成由 Agent（龙虾）完成，本脚本负责解析和保存。
"""

import os
import sys
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)


def parse_content_to_json(content_text):
    """
    将生成的方案文本解析为 JSON 格式

    Args:
        content_text: 方案文本

    Returns:
        list: 页面方案的 JSON 数组
    """
    pages = []
    current_page = {}

    lines = content_text.split('\n')

    for line in lines:
        line = line.strip()

        if line.startswith('【第') and '页' in line:
            if current_page:
                pages.append(current_page)
            current_page = {'页面类型': ''}
            continue

        if ':' in line or '：' in line:
            sep = '：' if '：' in line else ':'
            parts = line.split(sep, 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()

                field_map = {
                    '页面类型': '页面类型',
                    '标题文案': '标题文案',
                    '副标题文案': '副标题文案',
                    '正文文案': '正文文案',
                    '画面描述': '画面描述',
                    '文字位置': '文字位置',
                    '成品图生成提示词': '成品图生成提示词',
                }

                if key in field_map:
                    current_page[field_map[key]] = value

    if current_page:
        pages.append(current_page)

    return pages


def parse_caption_to_json(content_text):
    """
    将生成的发布文案解析为 JSON 格式

    Args:
        content_text: 文案文本

    Returns:
        dict: 包含标题、正文、标签的字典
    """
    result = {
        'title': '',
        'content': '',
        'hashtags': []
    }

    lines = content_text.split('\n')
    current_section = None
    current_content = []

    for line in lines:
        line = line.strip()

        if '【标题】' in line or line.startswith('标题：') or line.startswith('标题:'):
            current_section = 'title'
            current_content = []
            continue
        elif '【正文】' in line or line.startswith('正文：') or line.startswith('正文:'):
            if current_section == 'title' and current_content:
                result['title'] = '\n'.join(current_content).strip()
            current_section = 'content'
            current_content = []
            continue
        elif '【标签】' in line or line.startswith('标签：') or line.startswith('标签:'):
            if current_section == 'content' and current_content:
                result['content'] = '\n'.join(current_content).strip()
            current_section = 'hashtags'
            current_content = []
            continue

        if current_section and line:
            current_content.append(line)

    if current_section == 'title' and current_content:
        result['title'] = '\n'.join(current_content).strip()
    elif current_section == 'content' and current_content:
        result['content'] = '\n'.join(current_content).strip()
    elif current_section == 'hashtags' and current_content:
        hashtag_text = ' '.join(current_content)
        hashtags = re.findall(r'#\S+', hashtag_text)
        result['hashtags'] = hashtags

    return result


def main():
    """主函数 - 从 stdin 读取 Agent 生成的内容，解析并保存"""
    input_data = sys.stdin.read().strip()

    if not input_data:
        print("❌ 错误：请通过 stdin 传入内容")
        sys.exit(1)

    # 检测输入是 JSON 还是纯文本
    try:
        data = json.loads(input_data)
        if isinstance(data, dict) and 'pages' in data:
            # JSON 格式：包含图文方案
            pages = data['pages']
            caption_result = data.get('caption')
        elif isinstance(data, list):
            pages = data
            caption_result = None
        else:
            pages = parse_content_to_json(input_data)
            caption_result = None
    except json.JSONDecodeError:
        # 纯文本格式
        pages = parse_content_to_json(input_data)
        caption_result = None

    # 保存图文方案
    output_file = os.path.join(SKILL_DIR, 'generated_content.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    print(f"💾 图文方案已保存到：{output_file}")
    print(f"📋 共 {len(pages)} 页")

    # 保存发布文案
    if caption_result:
        caption_output_file = os.path.join(SKILL_DIR, 'generated_caption.json')
        with open(caption_output_file, 'w', encoding='utf-8') as f:
            json.dump(caption_result, f, ensure_ascii=False, indent=2)
        print(f"💾 发布文案已保存到：{caption_output_file}")

    # 输出 JSON
    print(json.dumps(pages, ensure_ascii=False, indent=2))
    if caption_result:
        print(json.dumps(caption_result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
