# Honcho 跨设备记忆同步参考

## 配置结构速查

Honcho 不是外部插件，是 Hermes 内置的 memory provider plugin。

### 位置

```
~/.hermes/hermes-agent/plugins/memory/honcho/
    __init__.py         — 插件入口，1328行
    client.py           — HonchoClientConfig @dataclass, 783行
```

### 关键配置项 (HonchoClientConfig)

| 配置字段 | 默认值 | 说明 |
|---------|--------|------|
| host | "hermes" | Honcho 服务名 |
| workspace_id | "hermes" | 工作空间 |
| api_key | None | **必填** — Honcho API 密钥 |
| base_url | None | 自建 Honcho 服务 URL（覆盖默认云服务） |
| environment | "production" | 环境名 |
| pin_peer_name | False | 是否固定 peer name（设为 True 可跨平台统一记忆） |
| enabled | False | 通过 memory.provider=honcho 自动设为 True |
| save_messages | True | 是否保存消息到 Honcho |
| write_frequency | "async" | 写入频率：async/turn/session/N |
| context_tokens | None | 自动注入的上下文预算（None=无上限） |
| recall_mode | "context" | 记忆检索模式：context/tools/hybrid |

### 配置文件位置

- `~/.hermes/config.yaml` — `memory.provider` 字段 + `honcho: {}` 配置节
- `~/.hermes/.env` — `HONCHO_API_KEY=xxx` 环境变量

## 已知问题

1. `hermes memory setup` 命令**不是配置向导**——它是检查当前 memory provider 状态并写入 config.yaml 的工具。选择 honcho 后，它只写 `memory.provider: honcho` 回 config，**不会提示填 api_key**。所以 api_key 必须事先在 .env 中配置好。

2. 没有 `hermes honcho` CLI 子命令——不像 `hermes config` 或 `hermes tools`，Honcho 没有独立交互命令。配置完成后，下次启动 Hermes 会话时自动加载。

3. 多设备同步时 possible race condition — 如果两个 Hermes 实例同时写入同一个 Honcho workspace，后写入的可能覆盖先写入的。建议单台使用。

## 注册 Honcho 账号：Cloudflare CAPTCHA 障碍

### 问题描述
Honcho 云服务（https://app.honcho.dev）的注册页面有 Cloudflare 人机验证（Turnstile），**无头浏览器无法自动通过**。尝试 `browser_click` 点击验证框会触发 "故障排除" 提示且不通过。

### 失败尝试记录
| 尝试方式 | 结果 | 原因 |
|---------|------|------|
| browser_navigate → 填写注册表单 → 点击 Cloudflare 框 | 失败 | Cloudflare Turnstile 检测到非人类流量，拒绝通过 |
| 同一页面使用 GitHub OAuth 登录 | 页面跳转但授权流程不完整 | OAuth 需要手动授权 |
| 同一页面使用 Google OAuth 登录 | 弹窗被浏览器策略阻止 | 无头浏览器无法处理弹窗 |
| curl POST 到 `/api/auth/register` | 被重定向到登录页 | 无公开 API 注册接口 |
| pip install honcho-ai SDK 调用注册 API | 失败 | Python 3.9 环境不兼容（Hermes 运行时） |

### 唯一可行方式
**用户手动在桌面浏览器中注册** — 在自己电脑的浏览器中打开 https://app.honcho.dev/login → Create Account → 手动完成 Cloudflare 验证 → 获取 API Key。

### API Key 填入方式
注册后获取的 API Key 写入 `.env`：
```bash
sed -i '' 's/^HONCHO_API_KEY=$/HONCHO_API_KEY=your-actual-key/' ~/.hermes/.env
```
然后切换 provider：
```bash
hermes config set memory.provider honcho
```

## 备选远程 Memory Provider（当 Honcho 注册受阻时）

如果 Honcho 注册受阻（如 Cloudflare 验证无法通过），以下其他 memory provider 也可用于跨设备记忆同步：

### provider 对比

| Provider | 是否需要注册 | 自托管 | 适用场景 |
|----------|------------|--------|---------|
| **honcho** | 需要 Cloudflare 验证的网页注册 | 支持 `base_url` 自建 | 官方推荐的跨设备方案 |
| **mem0** | 需要注册 app.mem0.ai | 不支持 | 功能丰富的记忆平台 |
| **retaindb** | 需要 API Key | 支持 `base_url` 自托管 | 轻量级远程记忆 |
| **hindsight** | API key / 本地均可 | 支持 | 灵活的混合方案 |
| **holographic** | 无需注册（本地） | — | 纯本地，不能跨设备 |
| **byterover** | 需要 API Key | — | — |

### 配置要点（通用模式）

所有远程 provider 的配置方式类似：
1. 在 `.env` 中设置对应的 API Key（如 `RETAINDB_API_KEY=xxx`）
2. 执行 `hermes config set memory.provider <name>`
3. 验证：`hermes memory status`

### 如何确认 provider 是否内置

不要先试 `hermes plugins install <name>`。先查：
```bash
hermes memory status   # 看 Installed plugins 列表
```
如果列表中有该 provider，说明已内置，只需配 key 和 config 即可。

### Honcho 支持自托管（base_url）

HonchoClientConfig 支持 `base_url` 参数，可以指向自建的 Honcho 服务器：
```
env: HONCHO_BASE_URL=https://your-honcho-server.com
```
当 `api_key` 和 `base_url` 任一配置即可启用。这对有自托管能力的团队是有价值的替代路径。

## 发现路径（供下次排查类似问题时参考）

当用户问"怎么装 honcho"或"配置 honcho"时：

1. ❌ 不要先试 `hermes plugins install honcho` — honcho 不是外部插件
2. ❌ 不要找 `hermes honcho` 命令 — 不存在
3. ✅ 直接查 config.yaml — `honcho: {}` 节已存在说明内置
4. ✅ 查 .env — `HONCHO_API_KEY=` 空壳已存在说明只需填 key
5. ✅ 源码在 `plugins/memory/honcho/` — 读 client.py 看 HonchoClientConfig 确认需要什么
6. ✅ 最终流程：注册 → 填 key → `hermes config set memory.provider honcho`
7. ⚠️ 如果注册被 Cloudflare 阻塞 → 让用户手动在真浏览器中完成注册 → 不要尝试自动绕过
8. ⚠️ 如果注册始终不可行 → 推荐备选 provider（retaindb 或 mem0）

## 当前用户的特殊需求

用户杨嘉阳有 Mac（办公）和 Windows（家用）两台 Hermes：
- Mac 端已配好 memory，存有组织架构、OA 配置、英语学习计划等
- 需要在 Windows 端也能读到这些记忆
- 两台设备不同时使用（可以错开时间），所以写入冲突风险低
