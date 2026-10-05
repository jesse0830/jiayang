#!/bin/bash
# 回答「这个 Hermes 客户端需要升级吗」—— 先取证，再下结论。
# 用法: bash check_update_status.sh [--fetch]
#   默认只读本地（不联网）；--fetch 会 git fetch origin/main（国内 gitcode，通常无需代理）
REPO="${HERMES_REPO:-$HOME/.hermes/hermes-agent}"
HH="${HERMES_HOME:-$HOME/.hermes}"
cd "$REPO" 2>/dev/null || { echo "❌ 找不到 $REPO"; exit 1; }
# macOS 没有 GNU timeout：用 perl alarm 包一层
T() { perl -e 'alarm shift; exec @ARGV' "$@"; }

APPR="$REPO/apps/desktop/release/mac-arm64/Hermes.app"

 echo "===== 0. 客户端自己缓存的判断（界面显示的就是它）====="
UC="$HH/.update_check"
if [ -f "$UC" ]; then
  echo "  .update_check  (mtime $(stat -f '%Sm' "$UC" 2>/dev/null)):"
  python3 - "$UC" <<'PY' 2>/dev/null || cat "$UC"
import json, sys, datetime
d = json.load(open(sys.argv[1]))
ts = d.get("ts")
print("    ver=%s  behind=%s  rev=%s  ts=%s" % (
    d.get("ver"), d.get("behind"), d.get("rev"),
    datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "?"))
print("    判据 updateAvailable = behind > 0  →",
      "会提示可更新" if (d.get("behind") or 0) > 0 else "提示已是最新")
print("    rev=null = 想用 GitHub compare API 拿精确数但失败，计数来自本地 rev-list")
PY
else
  echo "  （无 .update_check —— 客户端还没检查过，或 HERMES_HOME 不是 $HH）"
fi
echo "  .update_exit_code: $(cat "$HH/.update_exit_code" 2>/dev/null || echo 无)   (上次 update 退出码，0=正常)"

echo
echo "===== 1. 本机安装版本 ====="
echo "  HEAD        : $(git log -1 --format='%h %ci %s' 2>/dev/null)"
echo "  CLI 版本    : $(grep -m1 '__version__' hermes_cli/__init__.py 2>/dev/null)"
echo "  桌面app源码 : $(grep -m1 '\"version\"' apps/desktop/package.json 2>/dev/null | tr -d ' ,\"')"
echo "  已构建 app  : $(defaults read "$APPR/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo 未构建)"
echo "  已构建时间  : $(stat -f '%Sm' "$APPR/Contents/MacOS/Hermes" 2>/dev/null || echo -)"
echo "  Web UI 产物 : $(stat -f '%Sm' ui-tui/dist/entry.js 2>/dev/null || echo 无)"

echo
echo "===== 2. behind 计数是不是真的（banner.py 警告浅克隆会报假数）====="
if [ -f .git/shallow ]; then echo "  ⚠️ .git/shallow 存在（浅克隆）→ rev-list 计数不可信"; else echo "  .git/shallow 不存在（非浅克隆）✅"; fi
if MB=$(git merge-base HEAD origin/main 2>/dev/null); then
  if [ "$MB" = "$(git rev-parse HEAD)" ]; then
    echo "  merge-base = HEAD 自身 ✅ 本地是远端干净祖先（可快进，计数为真）"
  else
    echo "  ⚠️ merge-base=$MB ≠ HEAD（历史分叉，计数需谨慎）"
  fi
else
  echo "  ⚠️ 与 origin/main 无共同祖先 → 计数不可信"
fi
echo "  HEAD..origin/main = $(git rev-list --count HEAD..origin/main 2>/dev/null)"
echo "  origin/main..HEAD = $(git rev-list --count origin/main..HEAD 2>/dev/null)   ← 必须为 0 才是「纯落后」"

echo
echo "===== 3. 决定性对比：版本号（提交数只是辅助）====="
echo "  远端 CLI : $(git show origin/main:hermes_cli/__init__.py 2>/dev/null | grep -m1 '__version__' || echo 取不到)"
echo "  远端 app : $(git show origin/main:apps/desktop/package.json 2>/dev/null | grep -m1 '\"version\"' | tr -d ' ,\"' || echo 取不到)"
echo "  --- 落后的 release 提交 ---"
git log --oneline --no-decorate HEAD..origin/main -- hermes_cli/__init__.py 2>/dev/null | head -12

echo
echo "===== 4. 改动规模（估升级风险）====="
for p in gateway hermes_cli apps/desktop ui-tui; do
  printf "  %-12s %s\n" "$p" "$(git diff --shortstat HEAD origin/main -- $p 2>/dev/null)"
done
echo "  ⚠️ gateway 大改时，autostash 回填 gateway/platforms/weixin.py 极易冲突：升级前先备份并准备手动恢复"

echo
echo "===== 5. 网络与代理（拉代码 vs 下二进制，两条通道）====="
curl -s -o /dev/null --max-time 8 -w "  直连 github.com  : %{http_code}  %{time_total}s\n" https://github.com || echo "  直连 github.com  : 不通"
curl -s -o /dev/null --max-time 8 -w "  直连 gitcode.com : %{http_code}  %{time_total}s\n" https://gitcode.com || echo "  直连 gitcode.com : 不通"
LP=$(lsof -nP -iTCP:7897 -sTCP:LISTEN 2>/dev/null | tail -n +2 | head -1 | awk '{print $1" pid="$2}')
echo "  代理端口 7897   : ${LP:-未监听}"
scutil --proxy 2>/dev/null | grep -E 'HTTPEnable|HTTPSEnable' | sed 's/^/  /'
echo "  说明: origin=gitcode 国内可直连 → 拉代码不需代理；GitHub compare API 与 electron 下载需代理/镜像"

echo
echo "===== 6. 远端 ref 是否刷新 ====="
if [ "$1" = "--fetch" ]; then
  T 90 git fetch origin main 2>&1 | tail -2
  echo "  fetch 后 落后 origin/main = $(git rev-list --count HEAD..origin/main 2>/dev/null)"
else
  echo "  跳过（加 --fetch 才联网；上面的远端数据来自上次 fetch 的 ref）"
fi
