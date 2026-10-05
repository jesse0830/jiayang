---
name: industrial-device-protocols
description: "Use when finding a hardware protocol from a model number."
version: 1.0.0
platforms: [macos]
---

# Industrial Device Protocol Lookup (中国工业设备对接协议调研)

Use when the user needs to integrate an industrial hardware device (weighing controller/indicator,
PLC, sensor, meter) into their system and only has a model number + 说明书. Goal: find the
communication protocol (RS232/RS485/Modbus/current-loop) the software must speak.

## Key insight
For Chinese industrial instruments the protocol is usually IN the official 说明书 itself
(串行通讯接口 / 大屏幕 chapters), not in a separate "protocol doc". Download and read the
full manual before assuming you need to hunt elsewhere. The 参数菜单 (P-numbers) often
selects WHICH protocol mode the device emits — that menu IS part of the protocol spec.

## Workflow
1. **Identify the vendor from the model number.** E.g. XK3190-* = 上海耀华称重系统有限公司
   (yaohua.com.cn). Vendor name determines doc language and where manuals are hosted.
2. **Search**: `"<model> 通讯协议"` and `"<model> 说明书 RS232 RS485 串口"`.
   NOTE: web_search / web_extract may be unconfigured (Firecrawl key missing) — use
   browser_exec (Bing: `https://www.bing.com/search?q=<query>`) for discovery instead.
3. **Prefer direct PDF links** on vendor/dealer sites (e.g. `http://<dealer>.com/.../XK3190-A27E+说明书1.pdf`).
   百度文库 / CSDN / book118 pages are login/paywalled — only fall back to them.
4. **Download with curl** (some servers reject empty UA; plain HTTP triggers an approval prompt — expected):
   `curl -sL -o /tmp/device.pdf "<url>" -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"`
   then `file /tmp/device.pdf` to confirm it is really a PDF.
5. **Extract text with pymupdf** (13-page Chinese manuals = seconds):
   ```python
   import pymupdf   # `import fitz` is deprecated but still works as fallback
   doc = pymupdf.open("/tmp/device.pdf")
   for i, page in enumerate(doc):
       print(page.get_text())
   ```
6. **Mine these sections from the manual**:
   - 串行通讯接口: pinout (9-pin: 2=RXD, 3=TXD, 5=GND), baud rates, frame format (e.g. ASCII
     1 start + 8 data + 1 stop, no parity), cable distance.
   - 通讯方式/命令表: continuous-output frame formats (e.g. `ww000.000kg` 毛重/净重/皮重
     prefixes) and command-response tables (e.g. `R`=read weight, `T`=tare, `Z`=zero).
   - 参数菜单 (P-numbers): which parameter selects baud / output content / output mode.
   - 大屏幕/扩展接口: may be a DIFFERENT physical layer (e.g. 20mA current loop @600 baud) — do not confuse with RS232.
7. **Deliver**: copy the PDF into the project folder + write a protocol summary MD for the dev
   team (pinout, frame format, command table, parameter menu, working pyserial example code).

## Pitfalls
- Don't trust the search-result snippet; always read the extracted PDF text.
- Multiple protocol modes exist per device (continuous / stable-only / command / big-screen
  format) — the parameter menu decides which is active. Document the mapping.
- Chinese manuals OCR badly in some extractors; pymupdf get_text works on digitally-printed PDFs.
- RS232 (point-to-point, <20m) vs RS485/current-loop (long distance) are different wiring —
  check what the customer's site can provide before promising a serial solution.

## Reference
- references/xk3190-a27e.md — full protocol details for the XK3190-A27E weighing controller
  (帛飞特 纺织厂 project, 2026-08), worked example of this workflow + project file locations.
