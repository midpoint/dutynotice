#!/usr/bin/env python3
"""学期值班逻辑回归测试

运行方式:
    python3 test_dutynotice.py
    或
    python3 -m unittest test_dutynotice

设计说明:
    - 期望值均从 config.py 推导，本文件验证的是"轮换算法、边界条件、
      配置结构"，因此学期日期或值班名单更新后，本测试无需修改。
    - 唯一编码了业务需求的是 SafetyDutyTest.test_grade_group_counts
      （教师安全值班：初一 3 组，初二/初三各 4 组）。
      若该需求变更，请同步修改此测试。
"""

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    NIGHT_SHIFT_GROUPS,
    NIGHT_SHIFT_SUNDAY_ROSTER,
    ADMIN_DUTIES,
    SUNDAY_ADMIN_DUTIES,
    SAFETY_DUTY_GROUPS,
)
from dutynotice import (
    SEMESTER_START_DATE,
    SEMESTER_END_DATE,
    get_semester_week,
    get_all_duties,
    get_night_shift,
    get_admin_duty,
    get_sunday_admin_duty,
    get_safety_duty,
    is_in_semester,
    query_person,
)
from dingtalk import format_duties_for_dingtalk

START = SEMESTER_START_DATE


def week1_sunday() -> date:
    """开学后第1个周日（每周从周日开始）"""
    return START + timedelta(days=6 - START.weekday())


def week1_monday() -> date:
    """开学后第1个周一"""
    return START + timedelta(days=(0 - START.weekday()) % 7)


def week_sunday(n: int) -> date:
    """本学期第 n 周的周日"""
    return week1_sunday() + timedelta(weeks=n - 1)


def week_monday(n: int) -> date:
    """本学期第 n 周的周一"""
    return week1_monday() + timedelta(weeks=n - 1)


class SemesterBoundaryTest(unittest.TestCase):
    """学期边界"""

    def test_before_start_no_duties(self):
        self.assertFalse(is_in_semester(START - timedelta(days=1)))
        self.assertEqual(get_all_duties(START - timedelta(days=1)), [])

    def test_start_and_end_inside(self):
        self.assertTrue(is_in_semester(START))
        self.assertTrue(is_in_semester(SEMESTER_END_DATE))
        self.assertFalse(is_in_semester(SEMESTER_END_DATE + timedelta(days=1)))


class NightShiftTest(unittest.TestCase):
    """夜间值班：周一~周四每周1组（4组轮流），周日16人名单轮流"""

    def test_monday_to_thursday_group_members(self):
        """周一~周四分别取当周组内第0~3人"""
        # 周的划分从开学日起每7天一块，与自然周不对齐，因此按日期动态取组
        base = week_monday(2)
        for weekday in range(4):
            d = base + timedelta(days=weekday)
            group = NIGHT_SHIFT_GROUPS[(get_semester_week(d) - 1) % len(NIGHT_SHIFT_GROUPS)]
            duties = get_night_shift(d)
            self.assertEqual(len(duties), 1)
            self.assertEqual(duties[0]["name"], group[weekday])

    def test_four_week_group_cycle(self):
        """每周1组，4组轮流：第1周与第5周周一同一个人"""
        week1 = get_night_shift(week_monday(1))[0]["name"]
        week5 = get_night_shift(week_monday(5))[0]["name"]
        self.assertEqual(week1, week5)

    def test_sunday_roster_rotation(self):
        """周日16人名单轮流：第1/2个周日为名单第1/2人，第17个周日回到第1人"""
        self.assertEqual(get_night_shift(week_sunday(1))[0]["name"], NIGHT_SHIFT_SUNDAY_ROSTER[0])
        self.assertEqual(get_night_shift(week_sunday(2))[0]["name"], NIGHT_SHIFT_SUNDAY_ROSTER[1])
        self.assertEqual(get_night_shift(week_sunday(16))[0]["name"], NIGHT_SHIFT_SUNDAY_ROSTER[15])
        self.assertEqual(get_night_shift(week_sunday(17))[0]["name"], NIGHT_SHIFT_SUNDAY_ROSTER[0])

    def test_friday_saturday_empty(self):
        self.assertEqual(get_night_shift(week_monday(2) + timedelta(days=4)), [])  # 周五
        self.assertEqual(get_night_shift(week_monday(2) + timedelta(days=5)), [])  # 周六

    def test_metadata(self):
        duty = get_night_shift(week_sunday(2))[0]
        self.assertEqual(duty["duty_type"], "夜间值班")
        self.assertEqual(duty["time_range"], "21:30-次日7:00")


class AdminDutyTest(unittest.TestCase):
    """行政值班：周一~周五，每天每类别1人，按 weekday 固定取人"""

    def test_weekday_fixed_order(self):
        """周一取各组第1人，周二取第2人……周五取第5人"""
        n = 2
        base = week_monday(n)
        for weekday in range(5):
            duties = get_admin_duty(base + timedelta(days=weekday))
            self.assertEqual(len(duties), len(ADMIN_DUTIES))
            for d in duties:
                self.assertEqual(d["name"], ADMIN_DUTIES[d["location"]][weekday])

    def test_all_categories(self):
        duties = get_admin_duty(week_monday(2))
        self.assertEqual({d["location"] for d in duties}, set(ADMIN_DUTIES.keys()))

    def test_weekend_empty(self):
        self.assertEqual(get_admin_duty(week_sunday(2)), [])      # 周日
        self.assertEqual(get_admin_duty(week_sunday(2) + timedelta(days=6)), [])  # 周六


class SundayAdminDutyTest(unittest.TestCase):
    """周日行政值班：仅周日，每5周循环"""

    def test_sunday_only(self):
        self.assertEqual(get_sunday_admin_duty(week_monday(2)), [])

    def test_five_week_cycle(self):
        """第1周与第6周相同（取各组第1人），第5周取各组第5人"""
        for n in (1, 6):
            for d in get_sunday_admin_duty(week_sunday(n)):
                self.assertEqual(d["name"], SUNDAY_ADMIN_DUTIES[d["location"]][0])
        for d in get_sunday_admin_duty(week_sunday(5)):
            self.assertEqual(d["name"], SUNDAY_ADMIN_DUTIES[d["location"]][4])

    def test_all_categories(self):
        duties = get_sunday_admin_duty(week_sunday(2))
        self.assertEqual({d["location"] for d in duties}, set(SUNDAY_ADMIN_DUTIES.keys()))


class SafetyDutyTest(unittest.TestCase):
    """教师安全值班：各年级独立组数轮换（初一3组，初二/初三各4组）"""

    def test_grade_group_counts(self):
        """业务需求：初一 3 组，初二/初三各 4 组（需求变更时同步修改此测试）"""
        self.assertEqual(len(SAFETY_DUTY_GROUPS["初一"]), 3)
        self.assertEqual(len(SAFETY_DUTY_GROUPS["初二"]), 4)
        self.assertEqual(len(SAFETY_DUTY_GROUPS["初三"]), 4)

    def test_weekly_group_rotation(self):
        """每周换1组：第4周初一回卷到第1组，初二/初三用第4组；第5周初二/初三回卷"""
        for n in (1, 2, 3, 4, 5):
            d = week_monday(n)
            for grade, groups in SAFETY_DUTY_GROUPS.items():
                expected = groups[(n - 1) % len(groups)][0]
                duty = [x for x in get_safety_duty(d) if x["location"] == grade][0]
                self.assertEqual(duty["name"], expected)

    def test_weekday_mapping(self):
        """周一~周五取组内第0~4人"""
        base = week_monday(2)
        for weekday in range(5):
            d = base + timedelta(days=weekday)
            for grade, groups in SAFETY_DUTY_GROUPS.items():
                expected = groups[(get_semester_week(d) - 1) % len(groups)][weekday]
                duty = [x for x in get_safety_duty(d) if x["location"] == grade][0]
                self.assertEqual(duty["name"], expected)

    def test_weekend_empty(self):
        self.assertEqual(get_safety_duty(week_sunday(2)), [])
        self.assertEqual(get_safety_duty(week_sunday(2) + timedelta(days=6)), [])

    def test_metadata(self):
        duty = get_safety_duty(week_monday(2))[0]
        self.assertEqual(duty["duty_type"], "教师安全值班")
        self.assertEqual(duty["time_range"], "13:00-14:00")


class AllDutiesTest(unittest.TestCase):
    """get_all_duties 汇总"""

    def test_monday_total(self):
        # 1 夜间 + 行政类别数 + 安全年级数
        n = len(get_all_duties(week_monday(2)))
        self.assertEqual(n, 1 + len(ADMIN_DUTIES) + len(SAFETY_DUTY_GROUPS))

    def test_sunday_total(self):
        # 1 夜间 + 周日行政类别数
        n = len(get_all_duties(week_sunday(2)))
        self.assertEqual(n, 1 + len(SUNDAY_ADMIN_DUTIES))

    def test_saturday_empty(self):
        self.assertEqual(get_all_duties(week_sunday(2) + timedelta(days=6)), [])

    def test_duty_type_set(self):
        types = {d["duty_type"] for d in get_all_duties(week_monday(2))}
        self.assertEqual(types, {"夜间值班", "行政值班", "教师安全值班"})


class QueryPersonTest(unittest.TestCase):
    """query_person 查询"""

    def test_finds_person_on_duty_day(self):
        """某天值班的人，查询时该天必须出现"""
        d = week_monday(2)
        name = get_night_shift(d)[0]["name"]
        results = query_person(name, START, SEMESTER_END_DATE)
        self.assertTrue(any(r[0] == d for r in results))

    def test_unknown_person(self):
        self.assertEqual(query_person("不存在的人", START, SEMESTER_END_DATE), [])


class DingTalkFormatTest(unittest.TestCase):
    """钉钉消息格式：今日信息 + 明日值班预告"""

    def test_tomorrow_preview_appended(self):
        """明日预告追加在今日信息之后，用分隔线隔开"""
        today_duties = get_all_duties(week_monday(2))
        tomorrow_duties = get_all_duties(week_monday(2) + timedelta(days=1))
        content = format_duties_for_dingtalk(today_duties, "今天", tomorrow_duties, "明天")
        self.assertIn("### 今天", content)
        self.assertIn("### 明天（明天）", content)
        self.assertLess(content.index("### 今天"), content.index("### 明天（明天）"))
        self.assertIn("---", content)

    def test_no_tomorrow_block_when_empty(self):
        """不提供明日信息时，消息中不含明日预告"""
        content = format_duties_for_dingtalk(get_all_duties(week_monday(2)), "今天")
        self.assertNotIn("明天", content)

    def test_empty_today_still_shows_tomorrow(self):
        """今日无值班（如周六）时，仍应包含明日预告"""
        saturday = week_monday(2) + timedelta(days=5)
        sunday = saturday + timedelta(days=1)
        content = format_duties_for_dingtalk(
            get_all_duties(saturday), "今天",
            get_all_duties(sunday), "明天",
        )
        self.assertIn("今日无值班安排", content)
        self.assertIn("### 明天（明天）", content)


class ConfigStructureTest(unittest.TestCase):
    """配置结构完整性"""

    def test_groups_have_expected_size(self):
        for group in NIGHT_SHIFT_GROUPS:
            self.assertEqual(len(group), 4)
        self.assertEqual(len(NIGHT_SHIFT_SUNDAY_ROSTER), 16)
        for people in ADMIN_DUTIES.values():
            self.assertEqual(len(people), 5)
        for people in SUNDAY_ADMIN_DUTIES.values():
            self.assertEqual(len(people), 5)
        for grade_groups in SAFETY_DUTY_GROUPS.values():
            for group in grade_groups:
                self.assertEqual(len(group), 5)

    def test_no_duplicate_within_group(self):
        """安全值班组内不允许重名（夜间值班允许同人多次值班，不做此检查）"""
        for grade_groups in SAFETY_DUTY_GROUPS.values():
            for group in grade_groups:
                self.assertEqual(len(group), len(set(group)))

    def test_admin_and_sunday_categories_match(self):
        self.assertEqual(set(ADMIN_DUTIES.keys()), set(SUNDAY_ADMIN_DUTIES.keys()))


if __name__ == "__main__":
    unittest.main()
