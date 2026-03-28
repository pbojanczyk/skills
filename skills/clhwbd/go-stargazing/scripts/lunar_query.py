#!/usr/bin/env python3
"""
lunar_query.py — 农历/公历转换查询工具
用法：
  python3 lunar_query.py 2026-04-04
  python3 lunar_query.py 2026-04-04 2026-04-06
  python3 lunar_query.py --lunar 2026-1-1      # 农历查公历
  python3 lunar_query.py --range 2026-04-01 2026-04-07
  python3 lunar_query.py --moon-phase 2026-04-04  # 月相估算
"""
import sys
from lunarcalendar import Converter, Solar, Lunar

SYNODIC = 29.53058867

def solar_to_lunar_str(year, month, day):
    try:
        s = Solar(year, month, day)
        l = Converter.Solar2Lunar(s)
        return f"{year}-{month:02d}-{day:02d} = 农历{l.year}年{l.month:02d}月{l.day:02d}"
    except Exception as e:
        return f"错误: {e}"

def lunar_to_solar_str(year, month, day):
    try:
        l = Lunar(year, month, day, is_leap=False)
        s = Converter.Lunar2Solar(l)
        return f"农历{year}年{month}月{day} = 公历{s.year}-{s.month:02d}-{s.day:02d}"
    except Exception as e:
        try:
            l = Lunar(year, month, day, is_leap=True)
            s = Converter.Lunar2Solar(l)
            return f"农历{year}年(闰){month}月{day} = 公历{s.year}-{s.month:02d}-{s.day:02d}"
        except:
            return f"错误: {e}"

def moon_phase_desc(year, month, day):
    """估算月相（以2026年2月17日新月为基准近似）"""
    from datetime import date
    # 已知：2026年2月17日是新月(正月初一)
    ref = date(2026, 2, 17)
    target_date = date(year, month, day)
    try:
        days = (target_date - ref).days
        cycle_pos = days % SYNODIC
        pct = cycle_pos / SYNODIC * 100
        
        if pct < 1.8: phase = "🌑 新月"
        elif pct < 8.9: phase = "🌓 眉月"
        elif pct < 17.8: phase = "🌓 上弦月"
        elif pct < 26.7: phase = "🌕 盈凸月"
        elif pct < 35.6: phase = "🌕 满月(望)"
        elif pct < 44.4: phase = "🌖 亏凸月"
        elif pct < 53.3: phase = "🌗 下弦月"
        elif pct < 62.2: phase = "🌘 残月"
        elif pct < 71.1: phase = "🌑 晦月/新月前夕"
        else: phase = "🌑 新月"
        
        illumination = abs(50 - pct) / 50 * 100 if pct <= 50 else (pct - 50) / 50 * 100
        return f"月相: {phase} (约{illumination:.0f}%亮度) 距新月{cycle_pos:.1f}天"
    except Exception as e:
        return f"月相估算错误: {e}"

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "--moon-phase" and len(sys.argv) >= 3:
        y, m, d = map(int, sys.argv[2].split('-'))
        print(moon_phase_desc(y, m, d))
    
    elif cmd == "--lunar" and len(sys.argv) >= 3:
        parts = list(map(int, sys.argv[2].split('-')))
        if len(parts) == 3:
            print(lunar_to_solar_str(parts[0], parts[1], parts[2]))
        else:
            print("格式: --lunar YYYY-M-D")
    
    elif cmd == "--range" and len(sys.argv) >= 4:
        from datetime import datetime, timedelta
        start = datetime.strptime(sys.argv[2], "%Y-%m-%d")
        end = datetime.strptime(sys.argv[3], "%Y-%m-%d")
        current = start
        while current <= end:
            print(solar_to_lunar_str(current.year, current.month, current.day))
            current += timedelta(days=1)
    
    elif cmd == "--help":
        print(__doc__)
    
    else:
        # 假设是日期列表
        for arg in sys.argv[1:]:
            if '-' in arg:
                parts = list(map(int, arg.split('-')))
                if len(parts) == 3:
                    print(solar_to_lunar_str(parts[0], parts[1], parts[2]))
                    print("  ", moon_phase_desc(parts[0], parts[1], parts[2]))

if __name__ == "__main__":
    main()
