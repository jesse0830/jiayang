# 实战案例：jiayang 仓库瘦身 + Obsidian vault 拆仓（2026-09-21）

背景：用户要把 Obsidian vault 同步到 iPhone。vault 原本是私人文档仓库 `jiayang` 的子目录（`obsidian-vault/`），手机端 vault 根 ≠ 仓库根会静默丢笔记，且不该把简历/证件类文件拉到手机 → 拆成独立仓库。仓库 `.git` 已涨到 129M，clone/push 慢。

## 操作链（全部 exit 0）

1. 备份：`git bundle create ~/Documents/work/jiayang-backup-20260921.bundle --all` + `git bundle verify`
2. 拆仓：`git subtree split --prefix=obsidian-vault -b vault-split` → 在新目录 `git init` → `git remote add tmp` + `git fetch tmp vault-split` + `git reset --hard FETCH_HEAD` → `git remote remove tmp` → `git remote add origin git@github.com:jesse0830/obsidian.git` → `git push -u origin main`
3. 父仓库：`git add -A` + commit（删除残留文件）+ `git rm -r --cached obsidian-vault` + `.gitignore` 写入 `obsidian-vault/`
4. 瘦身：剔除历史中 8 个路径 / 9 个对象 / **119.1 MiB** 的旧文档（这些路径在工作区早已删除，但仍在历史里 → `git gc` 完全无效，必须 `filter-repo`）
5. 推送：`git push --force-with-lease`（filter-repo 后需重新 `git remote add origin`）

## 结果总账

| 对象 | 操作前 | 操作后 |
|---|---|---|
| 父仓库 `jiayang` `.git` | 129M | **13M** |
| 父仓库跟踪文件 | — | 23 |
| 新仓库 `obsidian` `.git` | — | 2.1M |
| 新仓库提交数 | — | 108（本地=远程，HEAD `a414f369`） |
| 新仓库跟踪文件 | — | 53 |

校验方式：`git ls-remote origin HEAD` 对比 `git rev-parse HEAD` 一致；远程文件数 53；远程抽查 `account.md`、`2026-09-18.md`、`data.json` 均在位（`git cat-file -e origin/main:<path>`）。

## 复发时的其他经验

- **`.gitignore` 与目录**：父仓库 `git rm -r --cached <dir>` 之后，`.gitignore` 里写 `<dir>/`（带斜杠）才忽略目录本身。
- **obsidian-git 插件不用改配置**：插件用 findRoot 逐级向上找最近的 `.git`，vault 独立成仓库后自然认到；提示用户重启 Obsidian 一次。
- **推送抖动**：父仓库一次 push 报错，`git ls-remote` 探到通道正常后原样重试即成功 —— 判定为 SSH 抖动，不要升级成 `--force`。
- **用户侧偏好**：这类不可逆操作先给「备份 → 重写 → 校验 → force-with-lease」的结果总账表格（操作前/后对比 + 恢复命令），并落一份 md 记录到 `99-软件工厂/98 hermes/`（用户指定的成果目录）。
