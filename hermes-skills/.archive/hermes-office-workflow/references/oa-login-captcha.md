# OA 登录 + 验证码识别（oa.smardaten.com）

用户在 OA 查数据（待报销金额、流程状态等）时的登录流程与全部坑。

## 登录页

- URL: `https://oa.smardaten.com/application/login/1640627701456342`
- 账号：`17705148484`（手机号格式，密码见 memory）
- 表单用 browser_snapshot 定位 ref（每次会话 ref 会变）：
  账号 textbox、密码 textbox、验证码 textbox、登录 button
- 验证码图片 = 页面上 `src` 以 `data:image` 开头的 `<img>`，其 src 格式
  `data:image/png;base64,<b64>`。**不要用 `img[src^="data:image"]` 死等**——用
  `[...document.querySelectorAll('img')].find(i => i.src && i.src.startsWith('data:image'))`。
- 登录失败时验证码会自动刷新（b64 长度变化），需要重取。

## 关键坑 1：browser_console 返回的长 base64 会静默损坏

从 browser_console 取长 base64 字符串，传到本地可能被截断/单字符改动。
症状：PNG 签名与 IEND 都在，但 IDAT chunk `CRC-MISMATCH`，PIL 打开报
`unrecognized data stream contents`。直接写文件 OCR 必失败。

**修复流程（本会话已验证两次，PNG 均修复为 valid）：**

1. 浏览器端按 500 字符分块，每块算 JS hash：
```js
(() => { const img=[...document.querySelectorAll('img')].find(i=>i.src&&i.src.startsWith('data:image'));
const b64=img.src.split(',')[1]; const blocks=[];
for(let i=0;i<b64.length;i+=500){const c=b64.slice(i,i+500);let h=0;
for(let j=0;j<c.length;j++){h=(h*33+c.charCodeAt(j))>>>0;}blocks.push([i,h]);}
return {len:b64.length, blocks:blocks}; })()
```
2. 本地（Python）对同样分块算 hash：`h=(h*33+ord(c)) % (2**32)`，逐块对比，
   找出 mismatch 的偏移。
3. 只重取损坏块：console 里 `b64.slice(start,start+500)` 单独返回，核对 hash 一致。
4. 本地替换该块后，校验 PNG chunk CRC（`zlib.crc32` vs 存储 CRC）全 OK 再 OCR。

注意：JS `(h*33+c)>>>0` 与 Python `% 2**32` 理论上一致；若个别块 hash 对不上而
内容看起来相同，可能只是 JS 浮点精度问题，重取该块核对即可。

## 关键坑 2：命令行内联长 base64 触发解析 bug

`python3 -c "...长b64..."` 内联大段 base64 会触发 Hermes lifecycle guard 的
`embedded null byte` 错误（exit -1）。**解法：一律用 write_file 写 .py 脚本再
terminal 执行**，不要把长数据内联进命令行。识别脚本也要写成文件。

## OCR：多引擎投票

- pytesseract：多阈值（100~200 步进 20）+ 多 psm（7/8/13）+ whitelist=字母数字，
  转灰度 → 放大 4x LANCZOS → 阈值二值化 → MedianFilter(3) 去噪。
- ddddocr：`DdddOcr(show_ad=False).classification(png_bytes)`，常比 tesseract 准
  （本会话 VNUG / hYhN 均由 ddddocr 给出最接近的 4 位结果）。
- 高阈值（180~200）下 tesseract 更稳定；4 位字母数字混合，**大小写敏感**。
- 观察：损坏 PNG 会导致 ddddocr 报 `unrecognized data stream contents`——先修
  base64 再 OCR，别在坏图上折腾。

## 重试纪律（用户偏好，2026-08 明确）

- 验证码有分歧 / 登录失败时，**最多重试 2 次**；连续失败就停下来如实告诉用户。
- 备选方案：让用户手动登录后报数字；或用户念出验证码。
- 用户说"不用再试了"就立即停止，绝不继续循环。
- 整体体验：识别流程再"聪明"，一旦让用户等太久 / 反复失败，用户会直接放弃，
  宁可先报进度 + 给备选。

## 流程速查

snapshot 定位表单 → 填账号密码 → 取 data:image b64（分块 hash 校验修复）→
PNG CRC 校验 → pytesseract+ddddocr 投票 → 填入 → 点登录 → 检查 url 是否跳转
（还停在 login 页 = 失败，验证码已刷新）→ 最多再试 2 次 → 报结果或给备选。
