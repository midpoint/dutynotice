# 学校值班提醒程序

学校各类值班安排查询工具，支持钉钉定时推送。

包含两大模块：

- **学期值班**（常规学期）：按算法轮换（周数 + 分组循环）
- **暑假值班**：按 `duty.txt` 固定排班表查询（带班领导 / 值班行政 / 保安）

## 功能

- 查看今天/指定日期的所有值班安排
- 查看本学期某周的值班安排
- 查询某人的所有值班日期
- 支持日期范围查询
- 钉钉群推送提醒（学期消息含今日 + 明日预告）

## 文件说明

```
dutynotice/
├── config.py            # 学期配置（学期时间、各类值班人员名单）
├── dutynotice.py        # 学期值班逻辑（周数计算、分组轮换）
├── cli.py               # 学期命令行界面
├── dingtalk.py          # 钉钉推送（学期/暑假共用）
├── send_duty.py         # 学期推送脚本（GitHub Actions）
│
├── duty.txt             # 暑假值班排班表（GBK 编码 CSV）
├── summer_config.py     # 暑假配置（日期范围、读取 duty.txt）
├── summer_duty.py       # 暑假值班逻辑（按日期查表）
├── summer_cli.py        # 暑假命令行界面
├── send_summer_duty.py  # 暑假推送脚本（GitHub Actions）
│
├── test_dutynotice.py   # 学期轮换算法回归测试
├── requirements.txt     # Python 依赖
└── .github/workflows/
    ├── duty.yml         # 学期推送（sparse checkout：仅学期所需文件）
    └── summer_duty.yml  # 暑假推送（含 duty.txt）
```

## 值班规则

| 类型 | 时间 | 安排 |
|------|------|------|
| 常规行政值班 | 周一到周五 7:00-21:40 | 分校级/初一/初二/初三 4 类，每类每天 1 人，按固定顺序轮换 |
| 教师安全值班 | 周一到周五 13:00-14:00 | 按年级独立分组轮换：初一年级 3 组（每 3 周循环），初二/初三各 4 组（每 4 周循环），每组 5 人、1 人/天、每组负责 1 周 |
| 周日行政值班 | 周日 18:00-21:40 | 每 5 周循环 |
| 夜间值班 | 周日到周四 21:30-次日 | 周日：16 人名单轮流（每 16 周一轮）；周一至周四：4 组轮流（每周 1 组、每组 4 人、1 人/天） |

## 本地使用

```bash
# 安装依赖
pip install -r requirements.txt

# ===== 学期值班 =====
python3 cli.py today                 # 查看今天值班
python3 cli.py date 2026-3-5         # 查看指定日期
python3 cli.py week                  # 查看本周
python3 cli.py week 3                # 查看第3周
python3 cli.py person 张三           # 查询某人所有值班
python3 cli.py range 2026-3-2 2026-3-8  # 查看日期范围
python3 cli.py help                  # 帮助
# 快捷命令：t / d / w / p（如 python3 cli.py t）

# ===== 暑假值班 =====
python3 summer_cli.py today                # 查看今天值班
python3 summer_cli.py date 2026-7-11       # 查看指定日期
python3 summer_cli.py range 2026-7-11 2026-7-20  # 查看日期范围
python3 summer_cli.py person 肖林军         # 查询某人值班
python3 summer_cli.py help                 # 帮助

# ===== 回归测试（验证轮换算法与配置结构）=====
python3 test_dutynotice.py

# ===== 本地测试钉钉推送 =====
DINGTALK_WEBHOOK=xxx DINGTALK_SECRET=xxx python3 send_duty.py
DINGTALK_WEBHOOK=xxx DINGTALK_SECRET=xxx python3 send_summer_duty.py
```

## 配置说明

修改 `config.py` 文件可自定义：

- `SEMESTER_START / SEMESTER_END` — 学期起止时间
- `NIGHT_SHIFT_GROUPS` — 夜间值班人员（周一至周四，4 组 × 4 人）
- `NIGHT_SHIFT_SUNDAY_ROSTER` — 周日夜间值班名单（16 人）
- `ADMIN_DUTIES` — 行政值班人员（校级/初一/初二/初三 4 类）
- `SUNDAY_ADMIN_DUTIES` — 周日行政值班人员
- `SAFETY_DUTY_GROUPS` — 教师安全值班分组（初一 3 组、初二/初三 4 组，按年级 keyed）

修改暑假排班请编辑 `duty.txt`（**GBK 编码** CSV，列：日期、带班领导、值班行政、保安1、保安2），日期范围在 `summer_config.py` 中调整。

## 钉钉推送

GitHub Actions 工作流（`duty.yml` / `summer_duty.yml`）推送值班提醒，schedule 定时已停用，当前通过以下方式触发：

- `workflow_dispatch` — GitHub 页面手动触发
- `repository_dispatch` — 外部定时服务（如 cron）调用 API 触发

需在仓库 Secrets 配置：

- `DINGTALK_WEBHOOK` — 钉钉机器人 Webhook 地址
- `DINGTALK_SECRET` — 钉钉机器人加签密钥

**消息内容**：

- 学期（`send_duty.py`）：今日值班安排 + 明日值班预告
- 暑假（`send_summer_duty.py`）：今天 + 明天值班安排（带班领导 / 值班行政 / 保安）
