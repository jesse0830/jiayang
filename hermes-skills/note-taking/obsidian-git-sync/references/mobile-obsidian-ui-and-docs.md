# 手机端 Obsidian：在哪点同步 + 官方文档怎么取

来源：2026-09-21 实取官方帮助文档源码（`help.obsidian.md/mobile` → 仓库 `obsidianmd/obsidian-help`），并用插件源码 `obsidian-git/main.js` 交叉验证命令名。

## 1. 手机端触发同步的四个入口

桌面版有 ribbon、有 Ctrl+P；手机版**两个都没有**。用户在手机上问「命令面板在哪里」时，直接给下面第 1 条。

1. **命令面板 = 从屏幕最顶端往下拉**（下拉手势）
   官方原文（`en/Getting started/Mobile app.md`）：
   > On the mobile app, you can define one action that gets invoked by **pulling down from the top of the app**, similar to how you would pull to refresh on social media apps. **Quick Action defaults to open Command palette.**

   拉出来后输入 `sync` → 选 **`Git: Commit-and-sync`**（obsidian-git 的命令一律带 `Git: ` 前缀；注意插件命令 id 是 `push` 但显示名是 `Commit-and-sync`，所以搜 sync 比搜 push 好使）。

2. **下拉拉出来的是别的东西** → 说明 Quick Action 被改过：设置 → **Options** → **Toolbar** → **Configure mobile Quick Action** → Configure → 输入 `Command palette` 选上。

3. ⭐ **推荐：把命令做成工具栏按钮**（一次设置，长期不用再翻面板）
   设置 → **Mobile** → **Manage toolbar options** → 滚到**最底** → **Add global command** → 输入 `Git: Commit-and-sync` → 选中。
   之后**编辑笔记时**底部那排图标里就多一个同步按钮（图标多了可左右滑动）。

4. **插件自己的入口**：
   官方原文：**"The mobile app has no Ribbon."** —— 手机端没有 ribbon，所有 ribbon 动作（含插件用 `addRibbonIcon` 加的 Git 图标）都收进**导航栏最右边的 `☰`（Open menu）**里。
   → 点 `☰` → 找 **Git**（图标 `git-pull-request`）→ 打开源码控制面板 → 里面有 commit / commit-and-sync 按钮。
   ⚠️ 官方原文：**"The navigation bar shows up when you're not editing the app"** —— 编辑笔记时导航栏不显示，先收起键盘/点空白处退出编辑。

## 2. 取官方 Obsidian 文档的可靠姿势

`help.obsidian.md` 是 Obsidian Publish 站点，**正文异步渲染**：`document.body.innerText` / 常规正文抓取会拿到空壳或目录，别在 DOM 上反复试，直接去读**文档源码仓库**。

```bash
export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897

# (a) 列 en 目录，找文件路径（返回 JSON，用 python 解 name/type，别 grep）
curl -s https://api.github.com/repos/obsidianmd/obsidian-help/contents/en

# (b) 取正文（raw 最省事）
curl -s "https://raw.githubusercontent.com/obsidianmd/obsidian-help/master/en/Getting%20started/Mobile%20app.md"
```

坑：
- **默认分支是 `master`，不是 `main`**（用 main 查 git/tree 会返回空，`仓库文件总数: 0`）。
- 手机相关页面在 `en/Getting started/Mobile app.md`；UI 概念另见 `en/User interface/…`、核心插件页在 `en/Plugins/…`。
- GitHub API 的 `contents/<dir>` 比 `git/tree?recursive=1` 好用于「找路径」；同一个 API 返回体直接 `json.load`，不要靠 grep 名字（大小写与转义会骗人）。
- 插件行为（对话框文案、命令 id/名称、设置项是否被 `gitReady` 门控）**不用猜文档**，直接读 `<vault>/.obsidian/plugins/obsidian-git/main.js`。

## 3. 验证闭环：从 Mac 回读远程，不信手机上的提示

```bash
cd ~/Documents/work/jiayang/obsidian-vault
git ls-remote origin | sed 's/^/  /'          # 服务端真值（绕开本地缓存）
git fetch origin --quiet
git log -5 --format='%h | %an | %ad | %s' --date=format:'%m-%d %H:%M'
```

判断规则：
- **`ls-remote` 的 `refs/heads/*` 与本地 HEAD 对比** → 不一致说明确实有远端更新；一致则没有新东西。
- 提交来自哪台设备看 `%an` + 时间（本用户两端统一身份 `JesseYoung`，靠时间/文件名区分）。
- **手机首次 Commit-and-sync 弹 "no changes" 属正常**（克隆不产生本地改动）→ 让用户改一篇笔记再跑；把这句提示当失败会误导排查方向。
- 桌面端自动提交是否在跑，看远程是否每隔几分钟出现新的 `vault backup: <时间>` 提交即可，不用去翻 App 界面。
