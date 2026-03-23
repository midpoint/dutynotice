# 学校值班提醒程序

学校各类值班安排查询工具，支持钉钉定时推送。

## 功能

- 查看今天/指定日期的所有值班安排
- 查看本周或指定周的值班安排
- 查询某人的所有值班日期
- 支持日期范围查询
- 钉钉群定时推送提醒

## 文件说明

```
dutynotice/
├── config.py       # 配置文件（学期时间、值班人员名单）
├── dutynotice.py   # 值班逻辑
├── cli.py          # 命令行界面
├── dingtalk.py     # 钉钉推送
├── send_duty.py    # 定时推送脚本
└── requirements.txt
```

## 本地使用

```bash
# 安装依赖
pip install -r requirements.txt

# 查看今天值班
python3 cli.py today

# 查看指定日期
python3 cli.py date 2026-3-5

# 查看本周或第N周值班
python3 cli.py week
python3 cli.py week 3

# 查询某人所有值班
python3 cli.py person 郭仕基

# 查看日期范围
python3 cli.py range 2026-3-2 2026-3-8

# 帮助
python3 cli.py help
```

## 配置说明

修改 `config.py` 文件可自定义：

- 学期起止时间
- 夜间值班分组
- 行政值班人员
- 周日行政值班人员
- 教师安全值班分组

## 值班规则

| 类型 | 时间 | 安排 |
|------|------|------|
| 常规行政值班 | 周一到周五 7:00-21:40 | 每天固定人员 |
| 教师安全值班 | 周一到周五 13:00-14:00 | 3组循环，每3周一轮 |
| 周日行政值班 | 周日 18:00-21:40 | 每5周循环 |
| 夜间值班 | 周日到周四 21:30-次日7:00 | 3组循环，每3周一轮 |

## 钉钉推送

GitHub Actions 定时任务每周日到周五早上6点自动推送。

需要配置的 Secrets：
- `DINGTALK_WEBHOOK` - 钉钉机器人 Webhook 地址
- `DINGTALK_SECRET` - 钉钉机器人加签密钥
