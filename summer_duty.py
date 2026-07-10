#!/usr/bin/env python3
"""暑假值班核心逻辑"""

from datetime import date, timedelta
from typing import Optional

from summer_config import (
    SUMMER_DUTIES,
    SUMMER_START_DATE,
    SUMMER_END_DATE,
)


def is_in_summer(d: date) -> bool:
    """检查日期是否在暑假期间"""
    return SUMMER_START_DATE <= d <= SUMMER_END_DATE


def get_summer_duty(d: date) -> Optional[dict[str, str]]:
    """
    获取某天的暑假值班信息

    返回: {"leader": str, "admin": str, "guard1": str, "guard2": str}
    或 None（不在暑假期间或无值班安排）
    """
    if not is_in_summer(d):
        return None
    return SUMMER_DUTIES.get(d)


def get_duty_summary(d: date) -> Optional[str]:
    """获取某天值班摘要文字"""
    duty = get_summer_duty(d)
    if not duty:
        return None
    return f"{duty['leader']}/{duty['admin']}/{duty['guard1']} {duty['guard2']}"


def query_person(name: str) -> list[tuple[date, dict[str, str]]]:
    """查询某人在暑假期间的所有值班"""
    results = []
    current = SUMMER_START_DATE
    while current <= SUMMER_END_DATE:
        duty = get_summer_duty(current)
        if duty:
            for key in ("leader", "admin", "guard1", "guard2"):
                if duty[key] == name:
                    results.append((current, duty))
                    break
        current += timedelta(days=1)
    return results
