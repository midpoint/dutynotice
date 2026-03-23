#!/usr/bin/env python3
"""钉钉推送通知"""

import os
import hmac
import hashlib
import time
import base64
import json
from datetime import datetime, date
from typing import TypedDict

import requests


class DingTalkMessage(TypedDict):
    msgtype: str
    markdown: dict


def get_dingtalk_sign(secret: str) -> tuple[str, str]:
    """
    获取钉钉签名
    签名算法：HmacSHA256 + Base64编码
    """
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = f'{timestamp}\n{secret}'
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return timestamp, sign


def send_dingtalk_message(
    webhook: str,
    secret: str,
    title: str,
    content: str
) -> bool:
    """
    发送钉钉消息
    """
    timestamp, sign = get_dingtalk_sign(secret)

    # 构建请求URL（包含签名）
    url = f"{webhook}&timestamp={timestamp}&sign={sign}"

    # 构建消息体
    message = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": content
        }
    }

    try:
        response = requests.post(url, json=message, timeout=10)
        result = response.json()
        if result.get("errcode") == 0:
            print("钉钉消息发送成功")
            return True
        else:
            print(f"钉钉消息发送失败: {result}")
            return False
    except Exception as e:
        print(f"钉钉消息发送异常: {e}")
        return False


def format_duties_for_dingtalk(duties: list, date_str: str) -> str:
    """格式化值班信息为钉钉markdown内容"""
    if not duties:
        return f"### {date_str}\n\n今日无值班安排"

    # 按类型分组
    night_duties = [d for d in duties if d["duty_type"] == "夜间值班"]
    admin_duties = [d for d in duties if d["duty_type"] == "行政值班"]
    sunday_duties = [d for d in duties if d["duty_type"] == "周日行政值班"]
    safety_duties = [d for d in duties if d["duty_type"] == "教师安全值班"]

    lines = [f"### {date_str}", ""]

    if admin_duties:
        lines.append("-===***===-")
        lines.append("")
        lines.append("【常规行政值班】（7:00-21:40）")
        for d in admin_duties:
            lines.append(f"- {d['location']}：{d['name']}")
        lines.append("")

    if safety_duties:
        lines.append("-===***===-")
        lines.append("")
        lines.append("【教师安全值班】（13:00-14:00）")
        for d in safety_duties:
            lines.append(f"- {d['location']}：{d['name']}")
        lines.append("")

    if sunday_duties:
        lines.append("-===***===-")
        lines.append("")
        lines.append("【周日行政值班】（18:00-21:40）")
        for d in sunday_duties:
            lines.append(f"- {d['location']}：{d['name']}")
        lines.append("")

    if night_duties:
        lines.append("-===***===-")
        lines.append("")
        lines.append("【夜间值班】（21:30-次日7:00）")
        for d in night_duties:
            lines.append(f"- {d['name']}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试发送
    webhook = os.environ.get("DINGTALK_WEBHOOK", "")
    secret = os.environ.get("DINGTALK_SECRET", "")

    if not webhook or not secret:
        print("请设置 DINGTALK_WEBHOOK 和 DINGTALK_SECRET 环境变量")
        exit(1)

    # 测试消息
    send_dingtalk_message(
        webhook=webhook,
        secret=secret,
        title="值班提醒测试",
        content="### 测试消息\n\n这是一条测试消息"
    )
