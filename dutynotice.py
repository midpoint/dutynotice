#!/usr/bin/env python3
"""学校值班提醒程序"""

from datetime import date, timedelta
from typing import TypedDict

from config import (
    SEMESTER_START,
    SEMESTER_END,
    NIGHT_SHIFT_GROUPS,
    ADMIN_DUTIES,
    SUNDAY_ADMIN_DUTIES,
)

# 转换日期字符串为 date 对象
SEMESTER_START_DATE = date.fromisoformat(SEMESTER_START)
SEMESTER_END_DATE = date.fromisoformat(SEMESTER_END)


class DutyInfo(TypedDict):
    name: str
    duty_type: str
    location: str
    time_range: str


def get_semester_week(d: date) -> int:
    """获取日期是本学期第几周（每周从周日开始，从1开始）"""
    if d < SEMESTER_START_DATE:
        return 0
    days_since_start = (d - SEMESTER_START_DATE).days
    return days_since_start // 7 + 1


def get_day_of_week(d: date) -> int:
    """获取周几（0=周一, 6=周日）"""
    return d.weekday()


def get_night_shift(d: date) -> list[DutyInfo]:
    """获取某天的夜间值班"""
    weekday = get_day_of_week(d)
    if weekday in [4, 5]:  # 周五、周六不值班，星期天(6)到星期四(3)值班
        return []

    week_num = get_semester_week(d)
    if week_num == 0:
        return []

    # 每周安排1组，3组循环
    group_index = (week_num - 1) % len(NIGHT_SHIFT_GROUPS)
    group = NIGHT_SHIFT_GROUPS[group_index]

    # 周日(6)到周四(3)，对应索引0-4
    # weekday: 0=周一, 1=周二, 2=周三, 3=周四, 6=周日
    # 需要的索引: 周日=0, 周一=1, 周二=2, 周三=3, 周四=4
    if weekday == 6:
        day_index = 0
    else:
        day_index = weekday + 1

    if 0 <= day_index < len(group):
        person = group[day_index]
        return [{
            "name": person,
            "duty_type": "夜间值班",
            "location": "学校",
            "time_range": "21:30-次日7:00"
        }]
    return []


def get_admin_duty(d: date) -> list[DutyInfo]:
    """获取某天的行政值班（周一到周五）"""
    weekday = get_day_of_week(d)

    # 周六、周日不是行政值班
    if weekday >= 5:
        return []

    week_num = get_semester_week(d)
    if week_num == 0:
        return []

    # 周一到周五，每天每类别安排1人，固定顺序
    # weekday: 0=周一, 1=周二, 2=周三, 3=周四, 4=周五
    # 直接用 weekday 作为索引，不循环

    duties = []
    for category, people in ADMIN_DUTIES.items():
        person = people[weekday]
        duties.append({
            "name": person,
            "duty_type": "行政值班",
            "location": category,
            "time_range": "7:00-21:40"
        })

    return duties


def get_sunday_admin_duty(d: date) -> list[DutyInfo]:
    """获取某天的周日行政值班"""
    if get_day_of_week(d) != 6:  # 不是周日
        return []

    week_num = get_semester_week(d)
    if week_num == 0:
        return []

    # 每5周循环
    cycle_week = (week_num - 1) % 5
    person_index = cycle_week % 5

    duties = []
    for category, people in SUNDAY_ADMIN_DUTIES.items():
        person = people[person_index]
        duties.append({
            "name": person,
            "duty_type": "周日行政值班",
            "location": category,
            "time_range": "18:00-21:40"
        })

    return duties


def get_all_duties(d: date) -> list[DutyInfo]:
    """获取某天的所有值班"""
    duties = []
    duties.extend(get_night_shift(d))
    duties.extend(get_admin_duty(d))
    duties.extend(get_sunday_admin_duty(d))
    return duties


def is_in_semester(d: date) -> bool:
    """检查日期是否在本学期内"""
    return SEMESTER_START_DATE <= d <= SEMESTER_END_DATE


def query_person(person_name: str, start: date, end: date) -> list[tuple[date, list[DutyInfo]]]:
    """查询某人在日期范围内的所有值班"""
    results = []
    current = start
    while current <= end:
        duties = [d for d in get_all_duties(current) if d["name"] == person_name]
        if duties:
            results.append((current, duties))
        current += timedelta(days=1)
    return results
