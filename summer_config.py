"""
暑假值班配置

从 duty.txt 加载值班安排表
"""

import csv
from datetime import date
from pathlib import Path

# ============ 暑假时间 ============
SUMMER_START = "2026-07-11"
SUMMER_END = "2026-08-30"

SUMMER_START_DATE = date.fromisoformat(SUMMER_START)
SUMMER_END_DATE = date.fromisoformat(SUMMER_END)

# ============ 值班表缓存 ============
# key: date, value: {"leader": str, "admin": str, "guard1": str, "guard2": str}
_SUMMER_DUTIES: dict[date, dict[str, str]] = {}


def _parse_chinese_date(s: str) -> date:
    """解析中文日期格式 '2026年7月11日'"""
    s = s.strip()
    year = int(s[:4])
    month = int(s.split("年")[1].split("月")[0])
    day = int(s.split("月")[1].split("日")[0])
    return date(year, month, day)


def load_summer_duties() -> dict[date, dict[str, str]]:
    """
    从 duty.txt 加载暑假值班表

    文件格式（GBK编码）：
        日期,带班领导,值班行政,保安1,保安2
        2026年7月11日,肖林军,陈名超,高卫权,王联山
        ...
    """
    if _SUMMER_DUTIES:
        return _SUMMER_DUTIES

    filepath = Path(__file__).parent / "duty.txt"
    if not filepath.exists():
        raise FileNotFoundError(f"值班表文件不存在: {filepath}")

    with open(filepath, encoding="gbk") as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过表头

        for row in reader:
            if not row or len(row) < 5:
                continue
            d = _parse_chinese_date(row[0])
            _SUMMER_DUTIES[d] = {
                "leader": row[1].strip(),
                "admin": row[2].strip(),
                "guard1": row[3].strip(),
                "guard2": row[4].strip(),
            }

    return _SUMMER_DUTIES


# 启动时加载
SUMMER_DUTIES = load_summer_duties()
