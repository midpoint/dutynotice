#!/usr/bin/env python3
"""学校值班提醒程序 - 命令行界面"""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# 添加当前目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent))

from dutynotice import (
    SEMESTER_START_DATE,
    SEMESTER_END_DATE,
    get_semester_week,
    get_all_duties,
    get_night_shift,
    get_admin_duty,
    get_sunday_admin_duty,
    is_in_semester,
    query_person,
)
from config import SEMESTER_START, SEMESTER_END


def format_date(d: date) -> str:
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return f"{d.year}年{d.month}月{d.day}日 {weekdays[d.weekday()]}"


def print_header(text: str):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print('='*50)


def cmd_today():
    """查看今天的值班"""
    today = date.today()

    if not is_in_semester(today):
        print(f"今天（{format_date(today)}）不在本学期时间内（{SEMESTER_START} 至 {SEMESTER_END}）")
        return

    week = get_semester_week(today)
    print_header(f"今天：{format_date(today)}（本学期第{week}周）")

    duties = get_all_duties(today)
    if not duties:
        print("今天没有值班安排")
        return

    # 按类型分组显示
    night = get_night_shift(today)
    admin = get_admin_duty(today)
    sunday = get_sunday_admin_duty(today)

    if night:
        print(f"\n🌙 夜间值班（21:30-次日7:00）：")
        for d in night:
            print(f"   {d['name']}")

    if admin:
        print(f"\n🏫 行政值班（7:00-21:40）：")
        for d in admin:
            print(f"   {d['location']}：{d['name']}")

    if sunday:
        print(f"\n📅 周日行政值班（18:00-21:40）：")
        for d in sunday:
            print(f"   {d['location']}：{d['name']}")


def cmd_date(date_str: str):
    """查看指定日期的值班"""
    try:
        # 支持格式：2026-3-2 或 2026.3.2 或 2026/3/2
        for sep in ['-', '.', '/']:
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    d = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    break
        else:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"日期格式错误，请使用：2026-3-2 或 2026.3.2 格式")
        return

    if not is_in_semester(d):
        print(f"日期（{format_date(d)}）不在本学期时间内（{SEMESTER_START} 至 {SEMESTER_END}）")
        return

    week = get_semester_week(d)
    print_header(f"{format_date(d)}（本学期第{week}周）")

    duties = get_all_duties(d)
    if not duties:
        print("没有值班安排")
        return

    night = get_night_shift(d)
    admin = get_admin_duty(d)
    sunday = get_sunday_admin_duty(d)

    if night:
        print(f"\n🌙 夜间值班（21:30-次日7:00）：")
        for d in night:
            print(f"   {d['name']}")

    if admin:
        print(f"\n🏫 行政值班（7:00-21:40）：")
        for d in admin:
            print(f"   {d['location']}：{d['name']}")

    if sunday:
        print(f"\n📅 周日行政值班（18:00-21:40）：")
        for d in sunday:
            print(f"   {d['location']}：{d['name']}")


def cmd_week(week_num: int):
    """查看本周值班"""
    today = date.today()
    current_week = get_semester_week(today)

    if week_num is None:
        week_num = current_week

    if week_num < 1 or week_num > 20:
        print("周数必须在1-20之间")
        return

    week_start = SEMESTER_START_DATE + timedelta(weeks=week_num - 1)

    print_header(f"本学期第{week_num}周值班安排")
    print(f"（{format_date(week_start)} 起）\n")

    for i in range(7):
        d = week_start + timedelta(days=i)
        if not is_in_semester(d):
            continue
        duties = get_all_duties(d)
        duty_str = ""
        if duties:
            for duty in duties:
                if duty_str:
                    duty_str += "，"
                duty_str += f"{duty['name']}({duty['duty_type']})"
        else:
            duty_str = "无"
        print(f"{format_date(d)}：{duty_str}")


def cmd_person(name: str):
    """查询某人的值班"""
    if not name:
        print("请提供姓名")
        return

    results = query_person(name, SEMESTER_START_DATE, SEMESTER_END_DATE)

    print_header(f"{name} 的值班安排")

    if not results:
        print("本学期内没有值班安排")
        return

    for d, duties in results:
        for duty in duties:
            print(f"{format_date(d)}：{duty['duty_type']}（{duty['location']}，{duty['time_range']}）")


def cmd_range(start_str: str, end_str: str):
    """查看日期范围内的值班"""
    try:
        start = datetime.strptime(start_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError:
        print("日期格式错误，请使用：2026-3-2")
        return

    if start > end:
        print("开始日期不能晚于结束日期")
        return

    print_header(f"{format_date(start)} 至 {format_date(end)} 值班安排")

    current = start
    while current <= end:
        duties = get_all_duties(current)
        if duties:
            print(f"\n{format_date(current)}：")
            for duty in duties:
                print(f"  {duty['name']} - {duty['duty_type']}（{duty['location']}，{duty['time_range']}）")
        current += timedelta(days=1)


def print_help():
    print("""
学校值班提醒程序

用法：
  python cli.py today                    查看今天值班
  python cli.py date 2026-3-5            查看指定日期值班
  python cli.py week 3                   查看本周或第N周值班
  python cli.py person 张三               查询某人所有值班
  python cli.py range 2026-3-2 2026-3-8  查看日期范围内值班
  python cli.py help                     显示帮助

快捷命令：
  python cli.py t                        等同于 today
  python cli.py d 2026-3-5              等同于 date
  python cli.py w 3                      等同于 week
  python cli.py p 张三                   等同于 person
""")


def main():
    if len(sys.argv) < 2:
        cmd_today()
        return

    cmd = sys.argv[1].lower()

    if cmd == "help" or cmd == "--help" or cmd == "-h":
        print_help()
    elif cmd == "today" or cmd == "t":
        cmd_today()
    elif cmd == "date" or cmd == "d":
        if len(sys.argv) >= 3:
            cmd_date(sys.argv[2])
        else:
            cmd_today()
    elif cmd == "week" or cmd == "w":
        week_num = int(sys.argv[2]) if len(sys.argv) >= 3 else None
        cmd_week(week_num)
    elif cmd == "person" or cmd == "p":
        if len(sys.argv) >= 3:
            cmd_person(sys.argv[2])
        else:
            print("请提供姓名：python cli.py person 张三")
    elif cmd == "range" or cmd == "r":
        if len(sys.argv) >= 4:
            cmd_range(sys.argv[2], sys.argv[3])
        else:
            print("请提供日期范围：python cli.py range 2026-3-2 2026-3-8")
    else:
        # 尝试当作日期处理
        cmd_date(sys.argv[1])


if __name__ == "__main__":
    main()
