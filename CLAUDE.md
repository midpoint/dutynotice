# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

学校值班提醒程序 - School duty notice system with DingTalk integration.

## Architecture

```
dutynotice/
├── config.py            # Semester configuration (dates, duty personnel)
├── dutynotice.py        # Semester duty logic (week calculation, rotation)
├── cli.py               # Semester CLI interface
├── dingtalk.py          # DingTalk webhook integration (shared)
├── send_duty.py         # Semester scheduled push (GitHub Actions)
│
├── duty.txt             # Summer duty schedule table (GBK encoded CSV)
├── summer_config.py     # Summer config — parses duty.txt
├── summer_duty.py       # Summer duty logic (date lookup)
├── summer_cli.py        # Summer CLI interface
├── send_summer_duty.py  # Summer scheduled push (GitHub Actions)
│
├── requirements.txt     # Python dependencies
└── .github/workflows/
    ├── duty.yml         # Semester workflow (06:00 Beijing, Sun-Fri)
    └── summer_duty.yml  # Summer workflow (05:30 Beijing, daily)
```

## Key Functions in dutynotice.py

- `get_semester_week(d)` - Get week number (starts from Sunday)
- `get_night_shift(d)` - Night shift (Sun: 16-person roster rotation; Mon-Thu: 4 groups cycle)
- `get_admin_duty(d)` - Admin duty (Mon-Fri, fixed daily)
- `get_sunday_admin_duty(d)` - Sunday admin duty (5-week cycle)
- `get_safety_duty(d)` - Teacher safety duty (Mon-Fri, 13:00-14:00, 3-week cycle)
- `get_all_duties(d)` - Get all duties for a date

## Configuration

All duty configuration is in `config.py`:
- `SEMESTER_START/SEMESTER_END` - Semester date range
- `NIGHT_SHIFT_GROUPS` - Night shift personnel, Mon-Thu (4 groups x 4 people)
- `NIGHT_SHIFT_SUNDAY_ROSTER` - Sunday night shift roster (16 people, one per Sunday)
- `ADMIN_DUTIES` - Admin duty personnel (4 categories)
- `SUNDAY_ADMIN_DUTIES` - Sunday admin personnel
- `SAFETY_DUTY_GROUPS` - Teacher safety duty (初一 3 groups, 初二/初三 4 groups, keyed by grade)

## Summer Module (暑假值班)

Files: `summer_config.py` / `summer_duty.py` / `summer_cli.py` / `send_summer_duty.py`

- Schedule source: `duty.txt` (GBK encoded CSV with columns: 日期,带班领导,值班行政,保安1,保安2)
- Date range: July 11 — August 30
- Lookup-based (not algorithmic rotation) — reads the fixed schedule from CSV

### Key Functions in summer_duty.py

- `get_summer_duty(d)` — Look up duty info for a date (returns dict or None)
- `is_in_summer(d)` — Check if date is in summer range
- `query_person(name)` — Find all summer duties for a person

### Message Format

Sent at 05:30 Beijing time, includes **today + tomorrow** duty info:
```
今天值班安排：
带班领导：X
值班行政：X
保    安：X  X
---
明天值班安排（X月X日 周X）：
带班领导：X
...
```

## Common Commands

```bash
# Semester (常规学期)
python3 cli.py today
python3 cli.py date 2026-3-5
python3 cli.py week 3
python3 cli.py person 张三

# Regression tests (验证轮换算法与配置结构)
python3 test_dutynotice.py

# Summer (暑假)
python3 summer_cli.py today
python3 summer_cli.py date 2026-7-11
python3 summer_cli.py range 2026-7-11 2026-8-30
python3 summer_cli.py person 肖林军

# Test DingTalk locally
DINGTALK_WEBHOOK=xxx DINGTALK_SECRET=xxx python3 send_duty.py
DINGTALK_WEBHOOK=xxx DINGTALK_SECRET=xxx python3 send_summer_duty.py
```

```bash
# Local usage
python3 cli.py today
python3 cli.py date 2026-3-5
python3 cli.py week 3
python3 cli.py person 张三

# Test DingTalk locally
DINGTALK_WEBHOOK=xxx DINGTALK_SECRET=xxx python3 send_duty.py
```

## Notes

- Week starts from Sunday (weekday=6)
- **Semester** GitHub Actions: `.github/workflows/duty.yml` — cron `45 20 * * *`, runs daily at Beijing 04:45 (UTC 20:45); message includes today's duties + tomorrow preview
- **Summer** GitHub Actions: `.github/workflows/summer_duty.yml` — runs at Beijing 05:30 (UTC 21:30), daily; message includes today + tomorrow
- Both workflows share the same DingTalk secrets (`DINGTALK_WEBHOOK`, `DINGTALK_SECRET`)
- `duty.txt` is GBK-encoded — always open with `encoding='gbk'`
- Semester uses algorithmic rotation (cycle-based); summer uses fixed table lookup (CSV-based)
