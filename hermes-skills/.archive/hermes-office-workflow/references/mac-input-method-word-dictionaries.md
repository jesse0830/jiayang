# Mac 中文输入法词库调查（微信输入法 / 搜狗）

调查时间：2026-08-20。结论：**微信输入法（WeType）不支持导入搜狗词库**。

## 安装位置

- 输入法装在**系统级** `/Library/Input Methods/`（不是用户级）：`SogouInput.app` + `WeType.app`
- 用户级 `~/Library/Input Methods/` 通常为空（只有 .localized）

## 数据目录

### 微信输入法（WeType）— `~/Library/Application Support/WeType/`
- `DataBase/common.db` — SQLite（表结构未公开，调查时 .tables 为空）
- `DictUpdate/DownloadDicts/cell_dict_*` — 下载词库，**cell 格式**（与搜狗细胞词库同名格式，但只是下载缓存，不代表支持导入）
- `userDict/v5/<timestamp>/` — **用户词库，LevelDB 格式**（.ldb/.log/MANIFEST），封闭格式
- `userDict/user_hot_word/` — 热词 LevelDB
- `mmkv/` — 配置（wetype.settings 等）
- 设置程序：`WeType.app/Contents/MacOS/WeTypeSettings.app`（zh-Hans.lproj/MainMenu.strings 是二进制 plist，用 `plutil -convert xml1` 查看）

### 搜狗输入法 — `~/Library/Application Support/Sogou/InputMethod/`
- `SogouPY/` — 用户数据（sgim_usr.bin、sgim_del_word.bin、sgim_eng_usr.bin 等**二进制用户词库**，私有格式）
- `SogouPY.users/00000001/` — 分用户词库数据
- `Backup/` — 备份目录

## 结论（已验证）

1. **无导入入口**：WeType.app / WeTypeSettings.app 二进制和 .strings 资源里没有「导入词库」相关 UI 字符串（grep 中文关键词「导入/词库/用户词典」无命中）
2. **格式封闭**：微信输入法用户词库是自有的 LevelDB 格式 + 微信账号云端同步，读不了搜狗的 bin/cell/txt
3. **官方口径**（网络资料）：微信输入法不支持直接导入第三方词库文件（txt/csv/自定义 bin 均不支持）；Windows 版也没有官方导入入口，只有「自定义短语」与账号同步
4. **替代方案**：
   - 保留搜狗为主力输入法（词库已积累，最省事）
   - 微信输入法重新养词库（自动学习 + 手动加自定义短语）
   - 解析搜狗 sgim_usr.bin 导出 txt 留档（未实施，可行但需解析私有格式）

## 调查技巧（复用）

- `strings <二进制> | grep 中文关键词` — 查主程序内置功能（中文按 UTF-8 可 grep 到）
- `.strings` 可能是二进制 plist：`file` 看类型 → `plutil -convert xml1 -o /tmp/out.xml <file>` 再 grep
- 找输入法数据目录：`ls ~/Library/Application\ Support/` + `find ~/Library -maxdepth 4 -iname "*sogou*"`
