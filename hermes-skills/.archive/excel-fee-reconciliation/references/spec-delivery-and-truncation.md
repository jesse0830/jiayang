# spec 交付 Excel 与长消息截断（26春 最终方案转 Excel 实测）

## 坑 1：merges 行号必须数准 rows 数组（含空行）

用 `xlsx_create.py` 的 JSON spec 生成交付表（sheet 名「最终方案」）时，`merges` 的行号按**实际 rows 数组位置**数（空行 `[]` 也算），不能按"第几大区块"猜。

- merge 覆盖到数据行会把该行非锚点单元格值吞掉（openpyxl 合并后只保留左上角值）
- 26春 实例：`A17:F17` 误合并到"社团"数据行、`A34:F34` 误合并到"R210 剩余"数据行，`xlsx_read.py --json` 读回这两处全是 null，而 spec 里明明有值
- 修复：对照 rows 数组重新数行号改 merges；**生成后逐值读回验证**（重点查被 merge 过的行、关键合计），别只看 sheet 名/维度正常就交付
- spec 中 `column_widths` 必须 dict 格式

## 坑 2：长汇总消息被截断

"Response remained truncated after 4 continuation attempts" = 模型单次输出超过 `model.max_tokens`（默认 8192）→ 系统自动续写 4 次 → 仍超长就报错。

- 根治：`hermes config set model.max_tokens 16384`（DeepSeek 实测接受 32768 上限；`deepseek-chat` 和 `deepseek-v4-flash` 都 OK）
- 先测 API 再改：读 `~/.hermes/.env` 的 `DEEPSEEK_API_KEY`，POST `https://api.deepseek.com/v1/chat/completions` 带 `max_tokens` 16384/32768 验证返回 OK
- 验证：`hermes chat -q "用中文写约1200字说明文字…"` 正常完成即通过
- 治标：长交付物生成文件，聊天只发摘要

## 26春 最终定稿数字（交付 Excel 内容基准）

- 弹性单价：二20 / 三27 / 四28 / 五30 / 六32（逐层上升，六年级最高）
- 分项合计（R2-R200）：早读 119020；午值 118660；晚辅 147710；过关 403440（含钱忠网1160）；弹性 282504（含钱忠网840）；社团 11040；优学 16500（含补算 19人109次=6540）；周末 10320；合计 **1109194**
- 总额对照：目标 1109833；差额 **639（用户接受，不超额）**；U总和 R203=1120194；R210 剩余=639
- 钱忠网：过关费 1700→**1160**（二23×40 + 三8×30）；弹性 840（二33×20 + 三6×30）
