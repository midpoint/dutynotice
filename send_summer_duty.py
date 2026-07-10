#!/usr/bin/env python3
"""发送暑假值班提醒到钉钉（每天 05:30 东八区）"""

import os
import sys
from datetime import date, datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from dingtalk import send_dingtalk_message
from summer_duty import get_summer_duty, is_in_summer


def get_china_date() -> date:
    """获取中国时区当前日期"""
    china_tz = timezone(timedelta(hours=8))
    now = datetime.now(china_tz)
    return now.date()


def format_duty_person(label: str, value: str) -> str:
    """格式化一行值班人员信息"""
    return f"**{label}**：{value}"


def build_notification(
    today_duty: dict[str, str],
    tomorrow_duty: dict[str, str] | None,
    today_str: str,
    tomorrow_str: str | None,
) -> str:
    """
    构建钉钉 Markdown 消息内容

    格式：
      ### 日期
      **今天值班安排：**
      - 带班领导：X
      - 值班行政：X
      - 保    安：X  X
      ---
      **明天值班安排（X月X日 周X）：**
      - 带班领导：X
      ...
    """
    lines = [f"### {today_str}", ""]

    # 今天
    lines.append("**今天值班安排：**")
    lines.append(f"- 带班领导：{today_duty['leader']}")
    lines.append(f"- 值班行政：{today_duty['admin']}")
    lines.append(f"- 保    安：{today_duty['guard1']} {today_duty['guard2']}")
    lines.append("")

    # 明天
    if tomorrow_duty and tomorrow_str:
        lines.append("---")
        lines.append("")
        lines.append(f"**明天值班安排（{tomorrow_str}）：**")
        lines.append(f"- 带班领导：{tomorrow_duty['leader']}")
        lines.append(f"- 值班行政：{tomorrow_duty['admin']}")
        lines.append(f"- 保    安：{tomorrow_duty['guard1']} {tomorrow_duty['guard2']}")

    return "\n".join(lines)


def main():
    webhook = os.environ.get("DINGTALK_WEBHOOK", "")
    secret = os.environ.get("DINGTALK_SECRET", "")

    if not webhook or not secret:
        print("错误: 请设置 DINGTALK_WEBHOOK 和 DINGTALK_SECRET 环境变量")
        sys.exit(1)

    today = get_china_date()
    tomorrow = today + timedelta(days=1)
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    if not is_in_summer(today):
        print(f"今天（{today}）不在暑假期间，跳过")
        sys.exit(0)

    today_duty = get_summer_duty(today)
    if not today_duty:
        print(f"今天（{today}）没有值班安排，跳过")
        sys.exit(0)

    # 构建日期字符串
    today_str = f"{today.year}年{today.month}月{today.day}日 {weekdays[today.weekday()]}"

    # 明天信息
    tomorrow_duty = get_summer_duty(tomorrow) if is_in_summer(tomorrow) else None
    if tomorrow_duty:
        tomorrow_str = f"{tomorrow.month}月{tomorrow.day}日 {weekdays[tomorrow.weekday()]}"
    else:
        tomorrow_str = None

    content = build_notification(today_duty, tomorrow_duty, today_str, tomorrow_str)

    print(f"=== 暑假值班提醒 ===")
    print(f"发送日期: {today_str}")
    print(f"今日值班: {today_duty['leader']} / {today_duty['admin']} / {today_duty['guard1']} {today_duty['guard2']}")
    if tomorrow_duty:
        print(f"明日值班: {tomorrow_duty['leader']} / {tomorrow_duty['admin']} / {tomorrow_duty['guard1']} {tomorrow_duty['guard2']}")

    success = send_dingtalk_message(
        webhook=webhook,
        secret=secret,
        title=f"🏖 暑假值班提醒 - {today_str}",
        content=content,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
