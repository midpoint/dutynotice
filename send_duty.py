#!/usr/bin/env python3
"""发送值班提醒到钉钉"""

import os
import sys
from datetime import date, datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from dingtalk import send_dingtalk_message, format_duties_for_dingtalk
from dutynotice import get_all_duties, get_semester_week, SEMESTER_END_DATE


def get_china_date():
    """获取中国时区当前日期"""
    china_tz = timezone(timedelta(hours=8))
    now = datetime.now(china_tz)
    return now.date()


def main():
    webhook = os.environ.get("DINGTALK_WEBHOOK", "")
    secret = os.environ.get("DINGTALK_SECRET", "")

    if not webhook or not secret:
        print("错误: 请设置 DINGTALK_WEBHOOK 和 DINGTALK_SECRET 环境变量")
        sys.exit(1)

    today = get_china_date()
    tomorrow = today + timedelta(days=1)
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    week_num = get_semester_week(today)
    date_str = f"{today.year}年{today.month}月{today.day}日 {weekdays[today.weekday()]} 第{week_num}周"

    duties = get_all_duties(today)

    # 明日值班预告（仅当明天仍在学期内且有值班时）
    tomorrow_duties = []
    tomorrow_str = None
    if tomorrow <= SEMESTER_END_DATE:
        tomorrow_duties = get_all_duties(tomorrow)
        if tomorrow_duties:
            tomorrow_week = get_semester_week(tomorrow)
            tomorrow_str = f"{tomorrow.month}月{tomorrow.day}日 {weekdays[tomorrow.weekday()]} 第{tomorrow_week}周"

    content = format_duties_for_dingtalk(duties, date_str, tomorrow_duties, tomorrow_str)

    print(f"=== 值班提醒 ===")
    print(f"发送日期: {date_str}")
    print(f"今日值班: {len(duties)} 条")
    if tomorrow_duties:
        print(f"明日预告: {tomorrow_str}, {len(tomorrow_duties)} 条")

    success = send_dingtalk_message(
        webhook=webhook,
        secret=secret,
        title=f"值班提醒 - {date_str}",
        content=content
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
