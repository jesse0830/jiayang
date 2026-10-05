---
name: english-learning-coach
description: "Guide Chinese-speaking users in creating and sustaining an English learning routine — diagnose level/goals, design a structured plan, set up daily reminders, and provide ongoing coaching via text-based practice."
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [language-learning, english, coaching, productivity]
    related_skills: [plan, cronjob]
---

# English Learning Coach

Help a Chinese-speaking user build and maintain an English learning habit. This covers the initial plan design and the ongoing daily coaching loop.

## When to Use

- User says "帮我制定英语学习计划" or "帮我练英语"
- User wants daily/weekly English practice with supervision
- User asks for English learning methods (listening, speaking, writing)

## Trigger Flow

### Step 1: Diagnose user needs
Ask these questions in order:
1. **Current level** — 初级 (Elementary) / 中级 (Intermediate) / 中高级 (Upper-Intermediate) / 高级 (Advanced)
2. **Focus area** — 职场英语 (Workplace), 口语对话 (Conversation), 阅读 (Reading), 写作 (Writing), 综合 (General)
3. **Daily time** — 15-20min / 30min / 45min+ / depends
4. **Schedule** — time of day (morning/lunch/evening) and days per week
5. **Preferred language** — 日常中文 + 英语练习模式, or 中英混合, or 全英文

### Step 2: Create a structured plan
Save as `/Users/jesseyoung/.hermes/english-plan.md` with:
- User profile summary (level, focus, schedule)
- Daily structure: Warm-up → New Input → Practice → Review
- Phased plan (recommend 3 phases of 4 weeks each, progressing from basics → scenarios → fluency)
- Grammar focus per phase
- Weekly theme breakdown

### Step 3: Set up daily reminder
Use `cronjob` with action='create':
- Schedule: matching user's preferred time (e.g. `0 20 * * *` for 8pm)
- Name: "英语练习日常提醒"
- Skills: [`hermes-agent`]
- Deliver: `origin`
- Prompt: gentle reminder text, ask user if they want to practice today, respect their choice

### Step 4: Daily coaching session

#### Format (text-only)
| Segment | Time | Content |
|---------|------|---------|
| Warm-up | 5min | Review previous day's words/phrases |
| New Input | 15min | Teach new workplace English vocab/sentences |
| Practice | 15min | Roleplay scenario — agent plays a character (colleague, client, boss), user responds in English. After each response, agent corrects and provides the better version. |
| Review | 10min | Summarize new words, common mistakes, key takeaways |

#### Before each practice session
Announce the switch: `"Now let's practice English:"` — then do the session in English.
After the review segment, switch back to Chinese.

#### Correction style
- Gentle, supportive, encouraging
- Format: repeat what user said correctly + brief rule explanation
- Do NOT interrupt the flow — quick note then continue

#### Example roleplay opener
```
Me: Hi! I'm Tom. I work in the Engineering team. What's your name?
User: (types response in English)
Agent: (corrects if needed, then continues the conversation)
```

### Step 5: Listening practice support
When user mentions listening resources:
- Recommend BBC Learning English (bbc.co.uk/learningenglish)
  - English In A Minute (elementary)
  - 6 Minute English (elementary→intermediate)
  - News Review (intermediate)
- Teach the 4-step listening method:
  1. **Blind listen** (3min) — no subtitles, just catch the gist
  2. **Read + listen** (5min) — with transcript, mark unknown words
  3. **Shadow** (5min) — pause and repeat each sentence
  4. **Summarize** (2min) — write new words, make sentences
- Offer to generate TTS audio of today's sentences: `text_to_speech(text="...")` → save, let user know the file path

### Step 6: Weekly review
Every weekend (Saturday or Sunday), do a mini review:
- New words and phrases learned this week
- Common recurring mistakes
- What to focus on next week

## Pitfalls

- **Do NOT default to English-only** — ask the user first. Most Chinese professionals prefer Chinese daily + English practice mode.
- **Text-only limitation** — there's no voice chat in Hermes CLI. Adapt practice to writing. Can use `text_to_speech` to generate audio for listening.
- **Apple Notes body format (critical)** — when using AppleScript to write into Notes.app, HTML tags (`<div>`, `<p>`, `<b>`, `<br>`) work but Apple Notes sometimes renders them inconsistently. The safest method: create the note first, then immediately overwrite its body with a well-formatted HTML string. Test by having the user open Notes.app and check.
- **Apple Notes duplicate notes** — when re-creating a note with the same name, the old note may persist. The `delete` command can fail with `can't get note...` error because AppleScript needs the exact reference. Workaround: iterate over `every note`, check `name of n`, and delete by content-matching (not just by name). Alternatively, accept the duplicate and have the user delete the old one manually.
- **Don't overwrite user's existing plan** — check if english-plan.md exists before creating.
- **Don't set cron reminders multiple times** — check existing cron jobs via cronjob list first.
- **WeChat (iLink Bot) delivery may be unreliable** — the cronjob's `deliver: weixin` may succeed on Hermes' end but the message never reaches the user's phone or PC WeChat. This manifests as silent failure: `send_message` returns success but user sees nothing. Causes include:
  - iLink Bot session token expiry / unauthorized user state (check gateway logs for `Unauthorized user` or `poll error: Server disconnected`).
  - Device sync limitations: PC WeChat does not auto-sync all messages from the phone account.
  - **Mitigation**: after setting up a cronjob with WeChat delivery, send a test message immediately and ask the user to confirm receipt. If delivery fails, switch to `origin` delivery (current Hermes chat).
- **Respect skip days** — if user says not today, say "好的，明天继续" and don't push.
- **Always verify cron delivery** — after creating or updating a reminder, send a test message via `send_message(target='weixin', message='test')` and ask user if they got it. Do not assume delivery works.
