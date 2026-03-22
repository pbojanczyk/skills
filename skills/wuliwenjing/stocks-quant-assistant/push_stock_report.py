#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时推送入口（供 launchd/cron 调用）
首次运行自动完成安装，之后直接执行分析
"""
import os
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)

# 触发自动安装（安装过则瞬间返回）
from stock_monitor import check_and_install, load_config, generate_report, push_report

def main():
    check_and_install()  # 幂等：已安装则立即返回
    mode = sys.argv[1] if len(sys.argv) > 1 else 'auto'
    config = load_config()
    report = generate_report(config, mode)
    push_report(report, config)

if __name__ == '__main__':
    main()
