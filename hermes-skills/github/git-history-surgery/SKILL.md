---
name: git-history-surgery
description: "Use when a git repo is too big or needs history rewrite."
version: 1.0.0
---

# Git History Surgery（仓库瘦身 / 拆分 / 历史重写）

**Trigger**：`.git` 太大导致 clone/push 慢或超时；删了大文件但体积不降；要把某个子目录拆成独立仓库（保留历史）；用户明确同意重写历史后强制推送。

这类操作**不可逆**且会改写 commit hash，顺序永远是：**先备份 → 再重写 → 后校验 → 最后 `--force-with-lease` 推送**。任何一步跳过都可能把用户的历史弄丢。

## 0. 先诊断，别急着承诺体积（最容易踩的坑）

".git 很大" 和 "删了文件还是不降" 有完全不同的原因：

```bash
cd <repo>
du -sh .git
git count-objects -vH                      # size-pack / count / in-pack
# 历史里最大的对象（blob = 文件内容）
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $3>1000000 {printf "%8.1f MB  %s\n", $3/1048576, $4}' \
  | sort -rn | head -30
# 每个路径在历史里占多少
git filter-repo --analyze && cat .git/filter-repo/analysis/*largest* 2>/dev/null
```

**`git gc --aggressive --prune=now` 对「历史里仍可达的旧 blob」无效**——对象还在 HEAD 的历史上，gc 不会删可达对象。若老文件是**曾经提交过、后来才删掉**的，只有重写历史（filter-repo）才能瘦下来。先跑上面的对象清单确认这一点，再告诉用户预期收益。

## 1. 备份（不可跳过）

```bash
cd <repo>
git bundle create ~/<repo>-backup-$(date +%Y%m%d).bundle --all
git bundle verify ~/<repo>-backup-$(date +%Y%m%d).bundle   # 必须 verify 通过再往下走
```

bundle 是**全量含所有分支的单个文件**，恢复：`git clone <bundle> <dir>`（远程 URL 用 `git remote add origin <url> && git fetch` 接回）。

## 2. 瘦身：git-filter-repo

macOS 不自带：`brew install git-filter-repo`（或 `pipx install git-filter-repo`）。

```bash
cd <repo>                                  # 建议在 clone 副本上做，原始目录留作最后保险
git filter-repo --path old/dir/ --path other/big.pptx --invert-paths   # 按路径从全历史剔除
git filter-repo --strip-blobs-bigger-than 1M                          # 按体积剔除
git filter-repo --strip-blobs-with-ids /tmp/blobs.txt                 # 按对象 id 精确剔除（上面对象清单导出即可）
```

**关键坑：`git filter-repo` 会移除 `origin` 远程**（防止误推重写后的历史）。重写完必须重新加回来再推：
```bash
git remote add origin <url>          # 或 git remote set-url origin <url>
git push --force-with-lease --all && git push --force-with-lease --tags
```
- 在非 fresh clone 上跑会报 "not a fresh clone"，加 `--force`。
- 只用 `--force-with-lease`，**绝不用裸 `--force`**；且必须先确认没有别人在这仓库上工作。
- 重写后 `.git` 体积立刻可见：`git count-objects -vH`。

## 3. 拆子目录成独立仓库（保留历史）

```bash
# 父仓库：把子目录历史抽成独立分支
cd <parent>
git subtree split --prefix=<subdir> -b <split-branch>

# 新仓库：取出该分支历史
mkdir <newdir> && cd <newdir> && git init -b main
git remote add tmp <parent-路径或url> && git fetch tmp <split-branch>
git reset --hard FETCH_HEAD && git remote remove tmp
git remote add origin git@github.com:<user>/<newrepo>.git
git push -u origin main

# 父仓库：取消跟踪 + 忽略（保留工作区文件，不是删文件）
cd <parent>
git rm -r --cached <subdir>
printf '%s/\n' '<subdir>' >> .gitignore
git commit -m "把 <subdir> 拆为独立仓库，父仓库不再跟踪"
```
父仓库提交历史里该子目录的旧对象仍在（体积不会因为这一步下降）——想同时瘦身要再做第 2 步。

## 4. 校验（推送前/后都要做）

推送前：
```bash
git log --oneline | wc -l                 # 提交数
git ls-tree -r --name-only HEAD | wc -l   # 跟踪文件数
du -sh .git
```
推送后**必须比对本地与远程真实状态**（不要只看 push 成功的输出）：
```bash
git ls-remote origin HEAD          # 远程 HEAD sha
git rev-parse HEAD                 # 本地 HEAD sha —— 两者必须相同
git ls-tree -r --name-only origin/main | wc -l        # 远程文件数
git cat-file -e origin/main:<某个关键文件> && echo "OK 文件在位"   # 抽查 2-3 个关键文件
git status --porcelain             # 干净
```
`--force-with-lease` 失败时先 `git ls-remote origin HEAD` 看远程是否被改过，再决定 `git fetch origin` 后重推，别直接升级成 `--force`。

## 5. 收尾

- 父仓库/新仓库都确认 `git status` 干净、`git log origin/main..HEAD` 为空。
- 桌面客户端（如 obsidian-git）用的 findRoot 会自然认到新的 `.git`，通常**无需改配置**；提示用户重启一次客户端更稳。
- **拆库后立刻查一次提交身份**：`git var GIT_AUTHOR_IDENT`。子仓库不会继承父仓库 `.git/config` 里的 `[user]`，漏设会静默退化（见 Pitfalls）。
- 记一份操作记录到用户的结果目录（改了哪些路径、哪些对象、体积对比、备份 bundle 路径、恢复命令）。

## Pitfalls

- **gc 治不了可达对象**（见第 0 节）——先诊断再动手。
- **filter-repo 会删掉 `origin`**，忘记重加 remote 会以为推送「莫名失败」。
- **重写历史 = 所有 commit hash 变化**：别人克隆过的仓库会冲突；只有用户明确同意、且这是他个人仓库时才做。
- **SSH 推送偶发失败 ≠ 通道坏了**：先 `git ls-remote origin` 探一次，再原样重跑一次往往就过（本用户实测过一次这样的抖动）。
- **`git rm -r --cached` 只取消跟踪，不删文件**；确认工作区文件还在再提交。
- **别用浅克隆（`--depth 1`）来达到「瘦身」的目的**：那只是本地的浅副本，远程和历史都没变。
- **拆出独立仓库后 git 身份会静默失效（本用户实测踩过）**：`[user]` 若原来只写在**父仓库的 `.git/config`**（即 `git config user.name` 没加 `--global`），新拆出的仓库没有这份配置 → git 退回自动推断的 `user@<主机名>.local` **假邮箱**。致命之处在于：**提交照旧成功、推送照旧成功**，但作者不归 GitHub 账号（不出现在贡献图、无法按人筛选、GitHub 认不出是他），不主动查根本发现不了。
  - 诊断用 `git var GIT_AUTHOR_IDENT`（看**实际生效**的身份），别只看 `git config user.email`——后者在没设值时也会安静地回显全局或空值。
  - 修复推荐设**全局**（一次管所有仓库）：`git config --global user.name "..."` + `git config --global user.email "<与仓库历史提交一致的作者邮箱>"`。
  - 校验闭环：让客户端（obsidian-git 等）**自己跑一次自动提交**，再 `git log -1 --format='%an <%ae>'` 确认作者已正确。
- 相关：网络通道问题（clone/push 超时、SSH 443）见 `github-china-access`；vault 拆分的业务背景见 `obsidian-git-sync`。

## 支持文件
- `references/jiayang-vault-split-and-slimming-20260921.md` — 实战案例：jiayang 仓库 129M→13M + vault 拆成独立仓库的完整数字与命令。
