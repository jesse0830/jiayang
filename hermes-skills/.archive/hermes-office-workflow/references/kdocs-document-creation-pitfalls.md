# 金山文档 (kdocs.cn) 网页版文档创建陷阱

## 问题描述

在 headless 浏览器中通过金山文档网页版（kdocs.cn）创建新文档时，"新建"按钮的下拉菜单为空，无法选择"文字"等文档类型。

## 导航路径

```
kdocs.cn/latest 主页 → 点击"新建"按钮 → 弹出 popover 菜单但为空
```

## 故障现象

- **browser_snapshot** 显示 `label-create__popover` 存在，但内部 `label-create__menu children=0`
- **browser_vision** 截图确认：hover 状态时弹出空白的白色小框（宽约100px，高约50px），无任何选项
- **browser_click** 无法触发菜单渲染：多种交互方式（mouseover、click、dispatchEvent）都无效
- 直接导航到 `kdocs.cn/create` 或 `kdocs.cn/office/new` → 空白页/只显示"返回首页"
- 无可用 REST API（curl 创建文档接口返回 404）
- 浏览器 console 无报错日志

## 根因分析

金山文档的"新建"菜单是 Vue SPA 组件，依赖鼠标 hover（而非 click）触发子菜单渲染。headless 浏览器可能缺少某些 DOM 事件（mouseenter）或动画帧，导致 Vue 的 `v-if`/`v-show` 条件渲染没有执行。

另外，金山文档的 SPA 架构可能做了用户代理检测或 Canvas 指纹检测——headless 浏览器可能被识别为自动化工具，从而跳过某些初始化渲染。

## 已知有效的替代方案

### 方案 A：本地编辑（推荐）
最可靠的方式，适合内容已准备好（如 Markdown 格式）：

1. 用户用本地编辑器（Typora、VS Code 等）直接打开 Markdown 文件
2. Hermes 协助生成内容，保存为本地 `.md` 文件
3. 用户手动复制内容到金山文档，或走其他协同路径

### 方案 B：飞书文档（替代协同平台）
如果用户有飞书账号，飞书文档是更好的替代选择：
- 有完整的 API 支持（通过 feishu_doc 工具）
- 支持 Markdown content blocks 写入
- 在 headless 浏览器中更可靠

### 方案 C：WPS API（需评估）
金山办公提供 WPS 开放平台 API，但需要：
- 注册开发者账号
- 创建应用获取 AppID + AppSecret
- 通过 REST API 创建/编辑文档
- 流程比飞书文档复杂，投入产出比低

## 何时放弃浏览器操作

以下情况出现 2-3 次后应主动建议改用本地工具：

| 信号 | 描述 | 建议 |
|------|------|------|
| 🚩 弹出菜单空白 | 点击"新建"后菜单无内容 | 立即建议本地编辑 |
| 🚩 直接 URL 空白 | `kdocs.cn/create` 等地址不渲染 | 改走 API 或本地 |
| 🚩 多次重试无效 | 换了交互方式（click/hover/JS）仍然一样 | 不要继续重试 |
| 🚩 用户说"太慢了" | 用户对浏览器操作速度不满 | 直接切本地方案 |

## 核心原则

**不要为了把一个文件放到一个特定平台上而反复尝试浏览器操作。** 如果目的只是修改文档内容，本地文件 + 手动上传是最快的路径。如果目的是自动化流程，先确认该平台有可用 API。

对于 Chinese Enterprise Web 办公平台（金山文档、腾讯文档、钉钉文档）：
- 优先查官方 API → 有 API 就走 API
- 无 API 或 API 门槛高 → 本地编辑 + 人工上传
- headless 浏览器作为最备选方案
