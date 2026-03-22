#!/usr/bin/env python3
"""发送值班提醒到钉钉"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

from dingtalk import send_dingtalk_message, format_duties_for_dingtalk
from dutynotice import get_all_duties


def main():
    webhook = os.environ.get("DINGTALK_WEBHOOK", "")
    secret = os.environ.get("DINGTALK_SECRET", "")

    if not webhook or not secret:
        print("错误: 请设置 DINGTALK_WEBHOOK 和 DINGTALK_SECRET 环境变量")
        sys.exit(1)

    today = date.today()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    date_str = f"{today.year}年{today.month}月{today.day}日 {weekdays[today.weekday()]}"

    duties = get_all_duties(today)
    content = format_duties_for_dingtalk(duties, date_str)

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
