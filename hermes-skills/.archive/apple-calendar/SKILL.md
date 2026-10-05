---
name: apple-calendar
description: "Add Apple Calendar events via osascript on macOS."
version: 1.0.0
created_by: agent
metadata:
  tags: [apple, calendar, osascript, schedule, macos]
  languages: [zh-CN, en]
---

# Apple Calendar 日程管理（osascript）

当用户说"加个日程 / 加个日历 / 本周五下午三点面试 / 安排个会议"时使用。**日程（Calendar event）≠ 提醒事项（Reminder）**——提醒用 `apple-reminders` 技能（remindctl），日程用本技能（Calendar + osascript）。

## 前提

- macOS + 日历 App。系统是中文的，日历名是中文（工作、个人、飞行计划 等）。
- 查日历列表：`osascript -e 'tell application "Calendar" to get name of every calendar'`

## 添加日程（标准做法）

```applescript
tell application "Calendar"
    tell calendar "工作"
        set startDate to current date
        set year of startDate to 2026
        set month of startDate to 8
        set day of startDate to 7
        set hours of startDate to 15
        set minutes of startDate to 0
        set seconds of startDate to 0
        set endDate to startDate + (1 * hours)
        make new event with properties {summary:"数据开发徐兆毅线下面试", start date:startDate, end date:endDate}
    end tell
end tell
```

- 用 `current date` + 逐字段 set 构造日期，**不要**用 `date "2026年8月7日 15:00:00"` 这种本地化字符串解析（系统区域设置不同会解析失败）。
- 结束时间 = 开始 + 时长（`startDate + (1 * hours)` = 1 小时）。
- 职场日程放"工作"日历；不确定时先查日历列表再选。

## 关键坑：`&` 字符串拼接会触发终端工具误判

osascript 里字符串拼接用 `&`（如 `summary of ev & linefeed & ...`），但 Hermes 的 terminal 工具会把命令里的 `&` 误判为后台运行标志而**拒绝执行**（报 "Foreground command uses '&' backgrounding"）。

**解决**：把 AppleScript 写到 .scpt 文件再执行：

```bash
# 1) write_file 写 /tmp/check_event.scpt
# 2) 执行
osascript /tmp/check_event.scpt
```

添加/修改事件本身（make new event、set 日期）不含 `&` 时可直接 heredoc 执行；凡是含 `&` 的读取/拼接脚本一律走 .scpt 文件。

## 验证

添加后查回事件确认：

```applescript
tell application "Calendar"
    set ev to first event of calendar "工作" whose summary is "数据开发徐兆毅线下面试"
    set out to "标题: " & (summary of ev) & linefeed & "开始: " & (start date of ev as string) & linefeed & "结束: " & (end date of ev as string)
    return out
end tell
```

输出应显示正确的 标题/开始/结束 时间。

## 用户习惯

- 用户（杨嘉阳，软件工厂厂长）常用场景：面试安排、会议日程。
- 加完后主动问要不要"提前提醒"（提前提醒属于提醒事项，用 remindctl/`--alarm` 或另设）和"补地点（会议室）"。
