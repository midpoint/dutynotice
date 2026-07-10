#!/usr/bin/env python3
"""暑假值班程序 - 命令行界面"""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from summer_duty import (
    get_summer_duty,
    is_in_summer,
    query_person,
)
from summer_config import SUMMER_START, SUMMER_END, SUMMER_START_DATE, SUMMER_END_DATE


def format_date(d: date) -> str:
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return f"{d.year}年{d.month}月{d.day}日 {weekdays[d.weekday()]}"


def print_header(text: str):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print("=" * 50)


def cmd_today():
    """查看今天值班"""
    today = date.today()

    if not is_in_summer(today):
        print(f"今天（{format_date(today)}）不在暑假期间（{SUMMER_START} 至 {SUMMER_END}）")
        return

    duty = get_summer_duty(today)
    print_header(f"🏖 今天：{format_date(today)}")

    if not duty:
        print("今天没有值班安排")
        return

    print(f"\n  带班领导：{duty['leader']}")
    print(f"  值班行政：{duty['admin']}")
    print(f"  保    安：{duty['guard1']}  {duty['guard2']}")

    # 同时显示明天
    tomorrow = today + timedelta(days=1)
    if is_in_summer(tomorrow):
        tomorrow_duty = get_summer_duty(tomorrow)
        if tomorrow_duty:
            print(f"\n  明天值班（{format_date(tomorrow)}）：")
            print(f"  带班领导：{tomorrow_duty['leader']}")
            print(f"  值班行政：{tomorrow_duty['admin']}")
            print(f"  保    安：{tomorrow_duty['guard1']}  {tomorrow_duty['guard2']}")


def cmd_date(date_str: str):
    """查看指定日期值班"""
    try:
        for sep in ["-", ".", "/"]:
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    d = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    break
        else:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"日期格式错误，请使用：2026-7-11 格式")
        return

    if not is_in_summer(d):
        print(f"日期（{format_date(d)}）不在暑假期间（{SUMMER_START} 至 {SUMMER_END}）")
        return

    duty = get_summer_duty(d)
    print_header(f"🏖 {format_date(d)}")

    if not duty:
        print("没有值班安排")
        return

    print(f"\n  带班领导：{duty['leader']}")
    print(f"  值班行政：{duty['admin']}")
    print(f"  保    安：{duty['guard1']}  {duty['guard2']}")


def cmd_range(start_str: str, end_str: str):
    """查看日期范围内值班"""
    try:
        start = datetime.strptime(start_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError:
        print("日期格式错误，请使用：2026-7-11 格式")
        return

    if start > end:
        print("开始日期不能晚于结束日期")
        return

    print_header(f"🏖 {format_date(start)} 至 {format_date(end)} 值班安排")

    current = start
    count = 0
    while current <= end:
        if is_in_summer(current):
            duty = get_summer_duty(current)
            if duty:
                print(f"\n{format_date(current)}:")
                print(f"  带班领导：{duty['leader']}")
                print(f"  值班行政：{duty['admin']}")
                print(f"  保    安：{duty['guard1']}  {duty['guard2']}")
                count += 1
        current += timedelta(days=1)

    if count == 0:
        print("范围内没有值班安排")


def cmd_person(name: str):
    """查询某人暑假值班"""
    if not name:
        print("请提供姓名")
        return

    results = query_person(name)
    print_header(f"🏖 {name} 的暑假值班安排")

    if not results:
        print("暑假期间没有值班安排")
        return

    for d, duty in results:
        roles = []
        if duty["leader"] == name:
            roles.append("带班领导")
        if duty["admin"] == name:
            roles.append("值班行政")
        if duty["guard1"] == name or duty["guard2"] == name:
            roles.append("保安")
        print(f"  {format_date(d)}：{'/'.join(roles)}")


def print_help():
    print("""
暑假值班提醒程序

用法：
  python summer_cli.py today                    查看今天值班
  python summer_cli.py date 2026-7-11           查看指定日期值班
  python summer_cli.py range 2026-7-11 2026-7-20 查看日期范围值班
  python summer_cli.py person 张三               查询某人值班
  python summer_cli.py help                     显示帮助

快捷命令：
  python summer_cli.py t                        等同于 today
  python summer_cli.py d 2026-7-11              等同于 date
  python summer_cli.py p 张三                   等同于 person
""")


def main():
    if len(sys.argv) < 2:
        cmd_today()
        return

    cmd = sys.argv[1].lower()

    if cmd in ("help", "--help", "-h"):
        print_help()
    elif cmd in ("today", "t"):
        cmd_today()
    elif cmd in ("date", "d"):
        if len(sys.argv) >= 3:
            cmd_date(sys.argv[2])
        else:
            cmd_today()
    elif cmd in ("range", "r"):
        if len(sys.argv) >= 4:
            cmd_range(sys.argv[2], sys.argv[3])
        else:
            print("请提供日期范围：python summer_cli.py range 2026-7-11 2026-7-20")
    elif cmd in ("person", "p"):
        if len(sys.argv) >= 3:
            cmd_person(" ".join(sys.argv[2:]))
        else:
            print("请提供姓名：python summer_cli.py person 张三")
    else:
        cmd_date(sys.argv[1])


if __name__ == "__main__":
    main()
