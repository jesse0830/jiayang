# 飞书 docx「两份方案融合成一份」工作流（实测可用）

场景：同一项目的两份设计方案（wiki 链接）→ 用个人应用整篇复制 A 作为承载页，再把 B 的差异内容按模块并入。
本次实例：A=《苏交科九江项目方案设计》，B=《九江综合管理设计方案》，成品《…（融合版）v1.0》（docx id 见会话）。

## 流程
1. 承载页：应用整篇复制 A（保留图片/表格），改标题、设权限（见 document-copy-workflow.md）。
2. 对齐：取双方页面 `children`（顶层块），用 `difflib.SequenceMatcher(None, Ak, Ck, autojunk=False).get_opcodes()`，`non-equal` 段即 B 的插入位置。**不要用两指针对比**——重复文本会错位。
3. 建块：用**逐层 children** 接口 `POST /docx/v1/documents/{doc}/blocks/{parent}/children`，body `{index, children:[payload…]}`，**返回真实 block_id**；先建父块拿 id，再给父块插子块（递归 fill）。**不要用 descendant 嵌套接口**：本应用下大面积 `1770001 invalid param`。
4. 位移：补插时插入位置只按**顶层块**递增（每个 root +1）。子树是插到 root 内部的，不改变顶层索引；按子树块数递增会把后续 root 推到错位置（本次曾把 root 推进「非功能设计」段，需事后定点清理）。
5. 限流：连续几百次写后会成批 `1770001`（**是限流不是内容错**，隔离实验证明同样载荷稍后单独插必然成功）。对策：root 之间 `sleep 8-25s`；单块重试 3-5 次、退避 45s；把每个 root 的写入包进 `try/except`。
- **`SSLEOFError: EOF occurred in violation of protocol` 连取 token 都会偶发崩**（`auth/v3/tenant_access_token/internal` 就挂）——脚本会在第一步 `exit=1` 什么都不做。外层必须能重跑（幂等设计），或给 `token()` 本身加 3 次重试；跑完必须核对输出末尾的 `DONE xxx` / `exit=`，不要只看「进程正常结束」。
6. 幂等续跑：① 快照 live → ② 从段首分割线后按序扫描，用 `startswith(want[:12])` 匹配 root → ③ 记录「缺失」与「有 root 但 0 子块的空壳」→ ④ 先降序删空壳 → ⑤ 重新快照，从光标处逐个补插（pos 只在成功时 +1）。
7. 保留段：删除逻辑必须按文本整段保留文首「融合说明」（否则 del 会把说明一起删掉）；重建说明用一条独立脚本按 index=1 插 6 块（heading2 + 5 段 text）。
8. 清理探针：定位/隔离实验会往正式文档插测试块——统一用唯一前缀（如 `probeX####`）标记，收尾自检 `probe blocks: 0`。

## 终检口径（一次跑完）
- 全量 difflib 列非 equal 段 → 查是否混入正文的重复残留（本次抓到 1 处孤立副本 + 9 处错位块）。
- 6 条分割线位置 + 每段首块期望文本比对（OK/MISMATCH）。
- B 文本节点覆盖率：`受检 N 缺失 0`（覆盖检查同时暴露深层子树没填：父块存在但 0 子块）。
- `probe blocks 0`；图片张数（本次 37/37）。

## 权限与交付
- 应用建的文档 `link_share_entity=tenant_readable`（同租户持链接可读），成员里只有应用本身是 `full_access`；用户可读可评论但不可编辑。
- 想让本人可编辑：`POST /drive/v1/permissions/{token}/members`（member_type=email/openid）或让用户「另存为副本」。
- `~/.hermes/.env` 的 FEISHU_APP_ID/SECRET 等凭据一律不回显、不写入文档。

## 根因备忘
- `kids()` 必须**优先读块顶层 `"children"`**，再退回类型键（`text`/`bullet`…）下的 children；读错字段会出现「脚本 exit 0 但内容从未插入」。
- callout/quote_container 在本应用下建不出来 → 降级为普通段落/无序列表；分割线走 children 批量路径。
- 分页 API：不带 `page_size` 有时返回 0 条 → 加 `"data" not in r` 守卫 + 重试（刷新 token）。
