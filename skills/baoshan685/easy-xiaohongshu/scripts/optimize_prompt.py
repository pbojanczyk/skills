#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词优化器 - 根据账号定位和需求，生成最适合的提示词
"""

import json
import sys
import os

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REFERENCES_DIR = os.path.join(SKILL_DIR, 'references')

def load_style_presets():
    """加载风格预设库"""
    preset_path = os.path.join(REFERENCES_DIR, 'style-presets.json')
    with open(preset_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_hashtag_library():
    """加载标签库"""
    hashtag_path = os.path.join(REFERENCES_DIR, 'hashtag-library.json')
    with open(hashtag_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def match_style_preset(account_type, presets):
    """
    根据账号类型匹配最佳风格预设
    
    Args:
        account_type: 账号定位（如：科技博主、亲子博主）
        presets: 风格预设库
    
    Returns:
        匹配的风格预设字典
    """
    # 直接匹配
    if account_type in presets['presets']:
        return presets['presets'][account_type]
    
    # 模糊匹配（提取关键词）
    keywords_map = {
        '科技': '科技博主',
        '数码': '科技博主',
        'AI': '科技博主',
        '亲子': '亲子博主',
        '育儿': '亲子博主',
        '宝妈': '亲子博主',
        '美妆': '美妆博主',
        '护肤': '美妆博主',
        '化妆': '美妆博主',
        '健身': '健身博主',
        '运动': '健身博主',
        '减脂': '健身博主',
        '美食': '美食博主',
        '烹饪': '美食博主',
        '做菜': '美食博主',
        '学习': '学习博主',
        '教育': '学习博主',
        '考研': '学习博主',
        '旅行': '旅行博主',
        '旅游': '旅行博主',
        '职场': '职场博主',
        '工作': '职场博主',
        '办公': '职场博主',
        '漫画': '漫画博主',
        '动漫': '漫画博主',
        '二次元': '漫画博主',
        '国漫': '漫画博主',
        '番剧': '漫画博主',
        '摄影': '摄影博主',
        '拍照': '摄影博主',
        '穿搭': '穿搭博主',
        '时尚': '穿搭博主',
        '游戏': '游戏博主',
        '电竞': '游戏博主',
        '音乐': '音乐博主',
        '歌手': '音乐博主',
    }
    
    for keyword, preset_name in keywords_map.items():
        if keyword in account_type:
            return presets['presets'].get(preset_name, presets['fallback'])
    
    # 无匹配，返回默认
    return presets['fallback']

def select_hashtags(content_direction, category_keywords, hashtag_library, count=10):
    """
    根据内容方向选择标签
    
    Args:
        content_direction: 内容方向
        category_keywords: 分类关键词映射
        hashtag_library: 标签库
        count: 标签数量
    
    Returns:
        标签列表
    """
    selected = []
    categories = hashtag_library['categories']
    
    # 1. 匹配垂直领域标签（2-3 个）
    for keyword, category_name in category_keywords.items():
        if keyword in content_direction:
            if category_name in categories:
                selected.extend(categories[category_name][:3])
            break
    
    # 2. 添加内容主题标签（3-4 个）
    if 'AI' in content_direction or '工具' in content_direction:
        selected.extend(categories.get('AI 工具', [])[:4])
    elif '教程' in content_direction:
        selected.extend(['#教程', '#干货分享', '#经验分享', '#新手必看'])
    elif '测评' in content_direction:
        selected.extend(['#测评', '#好物推荐', '#种草', '#避坑指南'])
    
    # 3. 添加通用热门标签（2-3 个）
    selected.extend(hashtag_library['通用热门标签'][:3])
    
    # 去重并限制数量
    unique_tags = []
    for tag in selected:
        if tag not in unique_tags:
            unique_tags.append(tag)
    
    return unique_tags[:count]

def generate_caption_prompt(account_type, content_direction, target_audience, topic, style_preset, hashtags):
    """
    生成小红书发布文案的提示词
    
    Args:
        account_type: 账号定位
        content_direction: 内容方向
        target_audience: 用户对象
        topic: 主题
        style_preset: 风格预设
        hashtags: 标签列表
    
    Returns:
        文案生成提示词字符串
    """
    # 读取文案模板
    caption_template_path = os.path.join(REFERENCES_DIR, 'caption-template.md')
    with open(caption_template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 填充模板
    caption_prompt = template.format(
        account_type=account_type,
        content_direction=content_direction,
        target_audience=target_audience,
        topic=topic,
        tone=style_preset['tone'],
        emoji=style_preset['emoji']
    )
    
    # 添加标签建议
    hashtag_section = "\n\n【标签】\n" + " ".join(hashtags)
    # 替换模板中的标签部分
    caption_prompt = caption_prompt.replace(
        "（10-12 个标签，格式：#标签 1 #标签 2 #标签 3 ...）",
        hashtag_section
    )
    
    return caption_prompt

def optimize_prompt(account_type, content_direction, target_audience, topic):
    """
    生成优化后的完整提示词（包含 8 页图文提示词 + 发布文案提示词）
    
    Args:
        account_type: 账号定位
        content_direction: 内容方向
        target_audience: 用户对象
        topic: 主题
    
    Returns:
        tuple: (image_prompt, caption_prompt, style_preset, hashtags)
            - image_prompt: 8 页图文生成提示词
            - caption_prompt: 发布文案生成提示词
            - style_preset: 匹配的风格预设
            - hashtags: 推荐标签列表
    """
    # 加载预设
    presets = load_style_presets()
    hashtag_library = load_hashtag_library()
    
    # 匹配风格
    style_preset = match_style_preset(account_type, presets)
    
    # 分类关键词映射（用于标签选择）
    category_keywords = {
        '科技': '科技',
        '数码': '科技',
        'AI': 'AI 工具',
        '工具': 'AI 工具',
        '软件': '科技',
        '亲子': '亲子',
        '育儿': '亲子',
        '教育': '学习',
        '美妆': '美妆',
        '护肤': '美妆',
        '化妆': '美妆',
        '健身': '健身',
        '运动': '健身',
        '美食': '美食',
        '烹饪': '美食',
        '学习': '学习',
        '考试': '学习',
        '旅行': '旅行',
        '旅游': '旅行',
        '职场': '职场',
        '工作': '职场',
        '漫画': '动漫',
        '动漫': '动漫',
        '二次元': '动漫',
        '国漫': '动漫',
        '番剧': '动漫',
    }
    
    # 选择标签
    hashtags = select_hashtags(content_direction, category_keywords, hashtag_library)
    
    # 读取 8 页图文模板
    template_path = os.path.join(REFERENCES_DIR, 'prompt-template.md')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 填充 8 页图文模板
    image_prompt = template.format(
        account_type=account_type,
        content_direction=content_direction,
        target_audience=target_audience,
        style=style_preset['style'],
        colors=style_preset['colors'],
        tone=style_preset['tone'],
        emoji=style_preset['emoji'],
        content_min=style_preset['content_length']['min'],
        content_max=style_preset['content_length']['max'],
        topic=topic
    )
    
    # 添加标签建议到图文提示词
    hashtag_section = "\n\n### 推荐标签\n" + " ".join(hashtags)
    image_prompt += hashtag_section
    
    # 生成发布文案提示词
    caption_prompt = generate_caption_prompt(
        account_type, content_direction, target_audience, topic, style_preset, hashtags
    )
    
    return image_prompt, caption_prompt, style_preset, hashtags

def main():
    """主函数 - 支持命令行调用"""
    if len(sys.argv) < 5:
        print("用法：python3 optimize_prompt.py <账号定位> <内容方向> <用户对象> <主题>")
        print("示例：python3 optimize_prompt.py \"科技博主\" \"AI 工具教程\" \"职场人、学生党\" \"OpenClaw 常见问题\"")
        sys.exit(1)
    
    account_type = sys.argv[1]
    content_direction = sys.argv[2]
    target_audience = sys.argv[3]
    topic = sys.argv[4]
    
    image_prompt, caption_prompt, style_preset, hashtags = optimize_prompt(
        account_type, content_direction, target_audience, topic
    )
    
    # 输出结果
    print("=" * 60)
    print("🎨 匹配风格预设")
    print("=" * 60)
    print(f"风格：{style_preset['style']}")
    print(f"色调：{style_preset['colors']}")
    print(f"语气：{style_preset['tone']}")
    print(f"表情符号：{style_preset['emoji']}")
    print(f"内容长度：{style_preset['content_length']['min']}-{style_preset['content_length']['max']}字")
    print()
    
    print("=" * 60)
    print("🏷️  推荐标签")
    print("=" * 60)
    print(" ".join(hashtags))
    print()
    
    print("=" * 60)
    print("📝 8 页图文生成提示词")
    print("=" * 60)
    print(image_prompt)
    print()
    
    print("=" * 60)
    print("📱 小红书发布文案生成提示词")
    print("=" * 60)
    print(caption_prompt)
    
    # 如果需要输出到文件，可以添加 --output 参数
    if len(sys.argv) > 5 and sys.argv[5] == '--output':
        output_dir = sys.argv[6] if len(sys.argv) > 6 else '.'
        with open(os.path.join(output_dir, 'image_prompt.txt'), 'w', encoding='utf-8') as f:
            f.write(image_prompt)
        with open(os.path.join(output_dir, 'caption_prompt.txt'), 'w', encoding='utf-8') as f:
            f.write(caption_prompt)
        print(f"\n✅ 提示词已保存到：{output_dir}/image_prompt.txt 和 {output_dir}/caption_prompt.txt")

if __name__ == '__main__':
    main()
