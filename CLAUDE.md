# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

学校值班提醒程序 - School duty notice system with DingTalk integration.

## Architecture

```
dutynotice/
├── config.py       # All configuration (semester dates, duty personnel)
├── dutynotice.py   # Core duty logic (week calculation, duty assignment)
├── cli.py          # Command-line interface
├── dingtalk.py     # DingTalk webhook integration
├── send_duty.py    # Scheduled push script for GitHub Actions
└── requirements.txt
```

## Key Functions in dutynotice.py

- `get_semester_week(d)` - Get week number (starts from Sunday)
- `get_night_shift(d)` - Night shift (Sun-Thu, 3 groups cycle)
- `get_admin_duty(d)` - Admin duty (Mon-Fri, fixed daily)
- `get_sunday_admin_duty(d)` - Sunday admin duty (5-week cycle)
- `get_safety_duty(d)` - Teacher safety duty (Mon-Fri, 13:00-14:00, 3-week cycle)
- `get_all_duties(d)` - Get all duties for a date

## Configuration

All duty configuration is in `config.py`:
- `SEMESTER_START/SEMESTER_END` - Semester date range
- `NIGHT_SHIFT_GROUPS` - Night shift personnel (3 groups)
- `ADMIN_DUTIES` - Admin duty personnel (4 categories)
- `SUNDAY_ADMIN_DUTIES` - Sunday admin personnel
- `SAFETY_DUTY_GROUPS` - Teacher safety duty (3 groups x 3 grades)

## Common Commands

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
- GitHub Actions workflow in `.github/workflows/duty.yml`
- Message format is in `dingtalk.py` `format_duties_for_dingtalk()`
