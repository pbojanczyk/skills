#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票量化监控系统 v6.0（通用版）
读取 config.yaml 获取股票池配置，无需硬编码
"""

import os
import sys
import yaml
import warnings
import requests
import subprocess
from datetime import datetime

warnings.filterwarnings('ignore')

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
MARKER_FILE = os.path.join(SKILL_DIR, '.installed')


# ============================================================
# 自动安装（首次运行时自动触发）
# ============================================================

def check_and_install():
    """检查依赖并在必要时自动安装，无须用户手动操作"""
    if os.path.exists(MARKER_FILE):
        return True  # 已安装

    print("[INFO] 首次运行，正在自动安装...", file=sys.stderr)

    # 1. 安装 akshare
    try:
        import akshare
        print(f"[INFO] akshare 已安装 ({akshare.__version__})", file=sys.stderr)
    except ImportError:
        print("[INFO] 正在安装 akshare...", file=sys.stderr)
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'akshare', 'pyyaml', '--quiet'],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            print("[INFO] akshare 安装成功", file=sys.stderr)
        else:
            print(f"[WARN] akshare 安装失败: {result.stderr[:200]}", file=sys.stderr)

    # 2. 注册 launchd（macOS）
    if sys.platform == 'darwin':
        plist_path = os.path.expanduser('~/Library/LaunchAgents/com.openclaw.stock-monitor.plist')
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)
        os.makedirs(os.path.join(SKILL_DIR, 'logs'), exist_ok=True)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.stock-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{SKILL_DIR}/push_stock_report.py</string>
        <string>morning</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>15</integer></dict>
        <dict><key>Hour</key><integer>10</integer><key>Minute</key><integer>30</integer></dict>
        <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Hour</key><integer>14</integer><key>Minute</key><integer>50</integer></dict>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>{SKILL_DIR}/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>{SKILL_DIR}/logs/launchd.err</string>
</dict>
</plist>
"""
        try:
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            subprocess.run(['launchctl', 'load', plist_path], capture_output=True, timeout=10)
            print("[INFO] 定时任务已注册 (launchd)", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] launchd 注册失败: {e}", file=sys.stderr)

    # 3. 写 marker
    with open(MARKER_FILE, 'w') as f:
        f.write(datetime.now().isoformat())
    print("[INFO] 安装完成", file=sys.stderr)
    return True


# ============================================================
# 配置加载
# ============================================================

def load_config():
    """加载配置文件（优先读 config.local.yaml，其次 config.yaml）"""
    local_path = os.path.join(SKILL_DIR, 'config.local.yaml')
    config_path = os.path.join(SKILL_DIR, 'config.yaml')

    # 优先使用本地配置（个人使用，不发布）
    if os.path.exists(local_path):
        config_path = local_path
    elif not os.path.exists(config_path):
        # 生成默认配置
        default_config = """# 股票监控配置
# 修改此文件以添加您的股票

stocks: []

push:
  channel: "console"
  times:
    - "09:15"
    - "10:30"
    - "13:00"
    - "14:50"

  feishu:
    chat_id: ""

  telegram:
    chat_id: ""
    bot_token: ""

advanced:
  history_days: 60
"""
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(default_config)
        print(f"[INFO] 配置文件已创建: {config_path}", file=sys.stderr)
        print("[INFO] 请编辑 config.yaml 添加您想监控的股票", file=sys.stderr)

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# ============================================================
# 数据采集层
# ============================================================

SINA_HQ_HEADERS = {'Referer': 'https://finance.sina.com.cn'}


def get_realtime_sina(codes_markets):
    """新浪HQ接口获取实时行情"""
    if not codes_markets:
        return {}
    symbols = ','.join([f'{m}{c}' for c, m in codes_markets])
    try:
        url = f'https://hq.sinajs.cn/list={symbols}'
        r = requests.get(url, headers=SINA_HQ_HEADERS, timeout=5)
        r.encoding = 'gbk'
        lines = r.text.strip().split('\n')
        result = {}
        for line in lines:
            match = line.split('=')
            if len(match) < 2:
                continue
            key = match[0].split('_')[-1]
            vals = match[1].replace('"', '').split(',')
            if len(vals) < 10:
                continue
            try:
                result[key] = {
                    'name': vals[0],
                    'open': float(vals[1]),
                    'prev_close': float(vals[2]),
                    'current': float(vals[3]),
                    'high': float(vals[4]),
                    'low': float(vals[5]),
                    'volume': float(vals[8]),
                    'amount': float(vals[9]),
                    'pct': 0.0
                }
                pc = result[key]['prev_close']
                cur = result[key]['current']
                result[key]['pct'] = round((cur - pc) / pc * 100, 2) if pc else 0
            except (ValueError, IndexError):
                continue
        return result
    except Exception as e:
        print(f"[WARN] get_realtime_sina failed: {e}", file=sys.stderr)
        return {}


def get_market_index_sina():
    """获取大盘指数"""
    try:
        url = 'https://hq.sinajs.cn/list=sh000001,sz399001,sz399006,sh000688'
        r = requests.get(url, headers=SINA_HQ_HEADERS, timeout=5)
        r.encoding = 'gbk'
        text = r.text
        result = {}
        mappings = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指',
            'sh000688': '科创50'
        }
        for mcode, name in mappings.items():
            try:
                idx = text.find(f'hq_str_{mcode}')
                if idx == -1:
                    continue
                segment = text[idx:text.index('"', idx + 10)]
                vals = segment.split('"')[1].split(',')
                if len(vals) < 6:
                    continue
                current = float(vals[3])
                prev_close = float(vals[2])
                pct = round((current - prev_close) / prev_close * 100, 2) if prev_close else 0
                result[name] = {'price': current, 'pct': pct}
            except Exception:
                continue
        return result
    except Exception as e:
        print(f"[WARN] get_market_index_sina failed: {e}", file=sys.stderr)
        return {}


def get_hist_from_sina(code, market, days=60):
    """获取历史K线数据"""
    import akshare as ak
    symbol = f'{market}{code}'
    try:
        df = ak.stock_zh_a_daily(symbol=symbol, adjust='qfq')
        if df is not None and not df.empty:
            df = df.tail(days)
            df.columns = [col.strip() for col in df.columns]
            return df
    except Exception:
        pass
    try:
        df = ak.fund_etf_hist_sina(symbol=symbol)
        if df is not None and not df.empty:
            df = df.tail(days)
            df.columns = [col.strip() for col in df.columns]
            return df
    except Exception:
        pass
    return None


def get_us_index_sina():
    """获取隔夜美股"""
    import akshare as ak
    result = {}
    for mcode, name in [('.DJI', '道琼斯'), ('.IXIC', '纳斯达克'), ('.SPX', '标普500')]:
        try:
            df = ak.index_us_stock_sina(symbol=mcode)
            if df is not None and not df.empty:
                last = df.iloc[-1]
                prev = df.iloc[-2]
                pct = round((float(last['close']) - float(prev['close'])) / float(prev['close']) * 100, 2)
                result[name] = pct
        except Exception:
            pass
    return result


def get_sector_tencent():
    """腾讯行情获取行业板块涨跌"""
    import akshare as ak
    try:
        df = ak.stock_sector_spot()
        if df is None or df.empty:
            return {}
        if '板块' not in df.columns or '涨跌幅' not in df.columns:
            return {}
        df = df.sort_values('涨跌幅', ascending=False)
        top = df.head(5)
        bottom = df.tail(5)
        return {
            'top': [(str(row['板块']), round(float(row['涨跌幅']), 2)) for _, row in top.iterrows()],
            'bottom': [(str(row['板块']), round(float(row['涨跌幅']), 2)) for _, row in bottom.iterrows()]
        }
    except Exception as e:
        print(f"[WARN] get_sector_tencent failed: {e}", file=sys.stderr)
        return {}


def get_north_money():
    """北向资金"""
    import akshare as ak
    try:
        df = ak.fund_hk_fund_hist_em(symbol="北向资金")
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            total = float(latest.get('净买入', 0))
            return {'total': round(total/1e8, 2), 'source': '东方财富'}
    except Exception:
        pass
    try:
        df = ak.stock_hsgt_north_hold_stock_em(symbol="北向资金")
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            total = float(latest.get('净买入', 0))
            return {'total': round(total/1e8, 2), 'source': '同花顺'}
    except Exception:
        pass
    return {}


def get_stock_news(code, count=3):
    """获取个股新闻"""
    import akshare as ak
    try:
        df = ak.stock_news_em(symbol=code)
        if df is not None and not df.empty:
            news = []
            for _, row in df.head(count).iterrows():
                title = str(row.get('新闻标题', ''))
                date = str(row.get('发布时间', ''))[:10]
                if title and title != 'nan':
                    news.append(f"• {date} {title[:28]}")
            return news
    except Exception:
        pass
    return []


# ============================================================
# 技术指标层
# ============================================================

def calc_ma(close, periods=[5, 10, 20, 60]):
    return {f'ma{p}': round(float(close.tail(p).mean()), 2) for p in periods}


def calc_macd(close, fast=12, slow=26, signal=9):
    s = close.astype(float)
    ema_fast = s.ewm(span=fast, adjust=False).mean()
    ema_slow = s.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd_hist = (dif - dea) * 2
    dif_v = round(float(dif.iloc[-1]), 3)
    dea_v = round(float(dea.iloc[-1]), 3)
    hist_v = round(float(macd_hist.iloc[-1]), 3)
    cross = 'none'
    if len(dif) >= 2:
        cross = 'gold' if float(dif.iloc[-2]) < float(dea.iloc[-2]) and dif_v >= dea_v else \
                'death' if float(dif.iloc[-2]) > float(dea.iloc[-2]) and dif_v <= dea_v else 'none'
    return {'dif': dif_v, 'dea': dea_v, 'hist': hist_v, 'cross': cross}


def calc_rsi(close, period=14):
    s = close.astype(float).diff()
    gain = s.where(s > 0, 0).rolling(window=period).mean()
    loss = (-s.where(s < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return round(float((100 - 100 / (1 + rs)).iloc[-1]), 1)


def calc_bollinger(close, period=20):
    s = close.astype(float)
    mid = s.rolling(window=period).mean()
    std = s.rolling(window=period).std()
    upper, lower = mid + 2*std, mid - 2*std
    cur = float(s.iloc[-1])
    pos = 'lower' if cur <= float(lower.iloc[-1]) else 'upper' if cur >= float(upper.iloc[-1]) else 'middle'
    return {
        'upper': round(float(upper.iloc[-1]), 2),
        'mid': round(float(mid.iloc[-1]), 2),
        'lower': round(float(lower.iloc[-1]), 2),
        'position': pos
    }


def calc_vol_ratio(volumes, period=5):
    s = volumes.astype(float)
    avg = float(s.tail(period+1).iloc[:-1].mean())
    today = float(s.iloc[-1])
    return round(today/avg, 2) if avg > 0 else 1.0


def calc_support_resistance(highs, lows, period=20):
    h = highs.astype(float)
    l = lows.astype(float)
    return {
        'resistance': round(float(h.tail(period).max()), 2),
        'support': round(float(l.tail(period).min()), 2)
    }


def score_stock(ma, macd, rsi, bollinger, vol_ratio, pct_change):
    score = 0
    if ma['ma5'] > ma['ma10'] > ma['ma20'] > ma['ma60']: score += 2
    elif ma['ma5'] < ma['ma10'] < ma['ma20'] < ma['ma60']: score -= 2
    elif ma['ma5'] > ma['ma10']: score += 1
    else: score -= 1

    if macd['cross'] == 'gold': score += 2
    elif macd['cross'] == 'death': score -= 2
    elif macd['hist'] > 0: score += 1
    else: score -= 1

    if rsi < 35: score += 2
    elif rsi > 65: score -= 2
    elif rsi < 45: score += 1
    elif rsi > 55: score += 1

    if bollinger['position'] == 'lower': score += 2
    elif bollinger['position'] == 'upper': score -= 2

    if pct_change > 0 and vol_ratio > 1.3: score += 1
    elif pct_change < 0 and vol_ratio < 0.7: score -= 1

    return max(-10, min(10, score))


def get_signal_info(score):
    if score >= 7: return '🟢 强烈买入', score
    elif score >= 4: return '🟢 买入', score
    elif score >= -3: return '🟡 持有', score
    elif score >= -6: return '🔴 卖出', score
    else: return '🔴 强烈卖出', score


# ============================================================
# 报告生成层
# ============================================================

def generate_suggestion(score, macd, rsi, bollinger, position, current_price):
    """生成操作建议"""
    parts = []
    if score >= 7: parts.append("技术面很强，可以买入")
    elif score >= 4: parts.append("技术面不错，可轻仓试探")
    elif score >= -3: parts.append("技术面中性，建议观望")
    elif score >= -6: parts.append("技术面偏弱，考虑减仓")
    else: parts.append("技术面很弱，建议减仓或清仓")

    if macd['cross'] == 'gold': parts.append("MACD刚金叉，短线有机会")
    elif macd['cross'] == 'death': parts.append("MACD刚死叉，短线要小心")

    if rsi < 35: parts.append(f"RSI={rsi}严重超卖，可能反弹")
    elif rsi > 65: parts.append(f"RSI={rsi}偏热，小心回调")

    if position:
        cost = position['cost']
        qty = position['quantity']
        profit = (current_price - cost) * qty
        profit_pct = (current_price - cost) / cost * 100

        if profit > 0:
            target = cost * 1.15
            if current_price >= target: parts.append("已涨超成本15%，建议卖一半落袋")
            else: parts.append(f"持有，等涨到{target:.2f}再考虑减仓")
            stop = cost * 0.92
            parts.append(f"跌回{stop:.2f}考虑止损")
        else:
            stop_loss = current_price * 0.90
            if abs(profit_pct) > 20:
                parts.append("深套，建议躺平，不割肉也不加仓")
                parts.append(f"跌破{stop_loss:.2f}要止损")
            elif abs(profit_pct) > 10:
                parts.append("轻套，建议观望，不加仓")
            else:
                parts.append("微套，保持仓位，不急于操作")

    return "；".join(parts[:4])


def analyze_stock(stock, realtime, hist, news):
    """生成单个股票分析"""
    code = stock['code']
    name = stock['name']
    emoji = stock.get('emoji', '📊')
    position = stock.get('position')

    if not realtime:
        return f"{emoji} {name}（{code}）- 实时数据获取失败\n"

    current = realtime.get('current', 0)
    pct = realtime.get('pct', 0)

    if hist is None or len(hist) < 20:
        return f"{emoji} {name}（{code}）- 历史数据获取失败\n"

    close = hist['close']
    high = hist['high']
    low = hist['low']
    volume = hist['volume']

    ma = calc_ma(close)
    macd = calc_macd(close)
    rsi = calc_rsi(close)
    bollinger = calc_bollinger(close)
    vol_ratio = calc_vol_ratio(volume)
    sr = calc_support_resistance(high, low)

    score = score_stock(ma, macd, rsi, bollinger, vol_ratio, pct)
    signal_emoji, score_val = get_signal_info(score)

    pct_str = f"+{pct:.2f}%" if pct >= 0 else f"{pct:.2f}%"

    lines = []
    lines.append(f"{emoji} {name}（{code}）")
    lines.append(f"   现价: {current:.2f}  今日: {pct_str}")
    lines.append(f"   信号: {signal_emoji} ({score_val:+.0f}分)")

    trend = "多头" if ma['ma5'] > ma['ma10'] > ma['ma20'] else "空头" if ma['ma5'] < ma['ma10'] < ma['ma20'] else "震荡"
    macd_status = "金叉↑" if macd['cross'] == 'gold' else "死叉↓" if macd['cross'] == 'death' else "纠缠"
    lines.append(f"   技术: {trend} | MACD:{macd_status} | RSI:{rsi} | 量比:{vol_ratio}")
    lines.append(f"   布林: {bollinger['lower']}~{bollinger['upper']}（{'下轨' if bollinger['position']=='lower' else '上轨' if bollinger['position']=='upper' else '中轨'}）")
    lines.append(f"   支撑/压力: {sr['support']} / {sr['resistance']}")

    if position:
        cost = position['cost']
        qty = position['quantity']
        profit = (current - cost) * qty
        profit_pct = (current - cost) / cost * 100
        profit_str = f"+{profit:.0f}元" if profit >= 0 else f"{profit:.0f}元"
        pct_str2 = f"+{profit_pct:.1f}%" if profit_pct >= 0 else f"{profit_pct:.1f}%"
        lines.append(f"   💰 持仓: 成本{cost:.2f} | {profit_str}({pct_str2})")

    if news:
        lines.append(f"   📰 {' | '.join(news[:2])}")

    suggestion = generate_suggestion(score, macd, rsi, bollinger, position, current)
    lines.append(f"   💡 {suggestion}")

    return '\n'.join(lines) + '\n'


def generate_report(config, mode='auto'):
    """生成完整分析报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    hour = datetime.now().hour
    if hour < 10: period = "开盘前"
    elif hour < 12: period = "早盘"
    elif hour < 14: period = "午后"
    else: period = "尾盘"
    if mode != 'auto':
        period = {'morning': '开盘前', 'noon': '早盘', 'afternoon': '午后', 'evening': '尾盘'}.get(mode, period)

    stocks_cfg = config.get('stocks', [])
    if not stocks_cfg:
        return "⚠️ 股票池为空，请先在 config.yaml 中添加股票。"

    lines = []
    lines.append(f"📊 股票参考 - {period} {today}")
    lines.append("━" * 20)

    codes_markets = [(s['code'], s['market']) for s in stocks_cfg]
    rt_raw = get_realtime_sina(codes_markets)
    realtime = {}
    for key, val in rt_raw.items():
        code = key.replace('sz', '').replace('sh', '')
        realtime[code] = val

    market = get_market_index_sina()
    sectors = get_sector_tencent()
    us_index = get_us_index_sina()
    north = get_north_money()

    if market:
        mkt_str = ' | '.join([f"{k} {v['price']:.0f}({v['pct']:+.1f}%)" for k, v in market.items()])
        lines.append(f"📊 A股大盘: {mkt_str}")

    if us_index:
        us_str = ' | '.join([f"{k} {v:+.1f}%" for k, v in us_index.items()])
        lines.append(f"🌏 昨夜美股: {us_str}")

    if sectors:
        top3 = sectors.get('top', [])[:3]
        if top3:
            lines.append(f"📈 强势板块: " + ' | '.join([f"{n}({p:+.1f}%)" for n, p in top3]))
        bot3 = sectors.get('bottom', [])[:3]
        if bot3:
            lines.append(f"📉 弱势板块: " + ' | '.join([f"{n}({p:+.1f}%)" for n, p in bot3]))

    if north:
        total = north.get('total', 0)
        direction = "净买入" if total > 0 else "净卖出"
        lines.append(f"📊 北向资金: {direction} {abs(total)}亿")

    if market or us_index or sectors or north:
        lines.append("━" * 20)

    for stock in stocks_cfg:
        code = stock['code']
        market_code = stock['market']
        rt = realtime.get(code, {})
        hist = get_hist_from_sina(code, market_code, days=config.get('advanced', {}).get('history_days', 60))
        news = get_stock_news(code, count=2)
        lines.append(analyze_stock(stock, rt, hist, news))

    lines.append("━" * 20)
    lines.append("⚠️ 仅供参考，不构成投资建议")
    lines.append(f"生成时间: {datetime.now().strftime('%H:%M:%S')}")

    return '\n'.join(lines)


# ============================================================
# 推送层
# ============================================================

def push_report(report_text, config):
    """推送报告到指定渠道"""
    channel = config.get('push', {}).get('channel', 'console')

    if channel == 'console':
        print(report_text)
        return

    elif channel == 'feishu':
        # 由 OpenClaw agent 路由，无需手动推送
        print(report_text)
        return

    elif channel == 'telegram':
        tg_cfg = config.get('push', {}).get('telegram', {})
        bot_token = tg_cfg.get('bot_token', os.environ.get('TG_BOT_TOKEN', ''))
        chat_id = tg_cfg.get('chat_id', os.environ.get('TG_CHAT_ID', ''))
        if bot_token and chat_id:
            try:
                requests.post(
                    f'https://api.telegram.org/bot{bot_token}/sendMessage',
                    json={'chat_id': chat_id, 'text': report_text},
                    timeout=10
                )
                return
            except Exception as e:
                print(f"[WARN] Telegram push failed: {e}")
        print(report_text)
        return

    else:
        print(report_text)


# ============================================================
# 主入口
# ============================================================

def main():
    # 首次运行自动安装（安装过则跳过）
    check_and_install()

    mode = sys.argv[1] if len(sys.argv) > 1 else 'auto'
    config = load_config()
    report = generate_report(config, mode)
    push_report(report, config)


if __name__ == '__main__':
    main()
