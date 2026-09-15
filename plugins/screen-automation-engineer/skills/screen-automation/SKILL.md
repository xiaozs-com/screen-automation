---
name: screen-automation
version: 1.1.42
display_name: 屏幕自动化
display_name_en: Screen Automation
description_zh: 增强 Agent 的屏幕理解和控制能力，利用本地屏幕视觉技术提高界面识别与定位效率；基于屏幕自动化小助手在 Windows 或 macOS 上确认目标窗口并安全完成当前屏幕任务。
description_en: Enhances an agent's screen understanding and control with local screen-vision technology, and uses Screen Automation Helper for safe screen tasks on Windows and macOS.
description: 增强 Agent 的屏幕理解和控制能力，利用本地屏幕视觉技术提高界面识别与定位效率；基于屏幕自动化小助手在 Windows 或 macOS 上确认目标窗口并安全完成当前屏幕任务。
metadata:
  slug: screen-automation
  version: 1.1.42
  displayName: 屏幕自动化
  summary: 增强 Agent 屏幕理解与控制的本地屏幕自动化能力
  homepage: https://www.xiaozs.com/sah/
---

# 屏幕自动化

使用“屏幕自动化小助手”完成当前屏幕任务，并为流程工程提供唯一的 CLI、能力、安全和流程标准。
需要把任务沉淀为可复用流程、维护已有流程，或处理 `执行者：agent` checkpoint 时，应由“屏幕自动化工程师”角色负责执行；具体能力与约束仍以本 Skill 为准。

## 系统全景

系统由三个独立安装和升级的核心层组成：桌面平台负责本地感知与执行，Agent Skill 负责方法和安全
约束，经验流程负责可复用的业务步骤与验证。DSH 等面向特定 Agent 运行时的适配属于独立桥接交付物，
不是第四个核心层；应用增强、屏幕连接器和 Agent Provider 属于桌面平台的可选扩展。

分析能力时先分层，再分别盘点成熟度和缺口。新版桌面端用三个只读入口回答不同问题：

- `cli describe`：产品结构、运行特性和安全契约；
- `cli capabilities`：当前安装版本声明的 CLI/SDK 动作契约，不代表产品架构或可选组件状态；
- `cli access list`：能力门类、来源、授权、依赖和访问状态，不是完整动作清单。

调用方必须忽略 `cli describe` 中未知的新增字段。旧桌面端可能没有 `cli describe`：若该命令明确返回
不支持或未知命令，继续使用本节的三层摘要，并以 `cli capabilities`、`cli access list` 和 `cli health`
分别核对动作、访问状态和运行环境；不得因此把旧版输出误解为完整系统模型，也不得把缺少自描述命令
当成桌面动作能力缺失。

## 连接

先按本机平台取得小助手原生 CLI 路径并读取真实能力：

```powershell
$AppCli = & "<Skill目录>\scripts\resolve_cli.ps1"
& $AppCli cli status
& $AppCli cli describe
& $AppCli cli capabilities
& $AppCli cli access list
```

```bash
APP_CLI="$(bash "<Skill目录>/scripts/resolve_cli.sh")"
"$APP_CLI" cli status
"$APP_CLI" cli describe
"$APP_CLI" cli capabilities
"$APP_CLI" cli access list
```

不得猜测安装位置、递归扫描用户目录或绕过小助手改用其他输入工具。找不到桌面端时停止，并让用户自行
下载安装：Windows `https://www.xiaozs.com/sah/downloads/windows/latest`；macOS
`https://www.xiaozs.com/sah/downloads/mac/latest`。未经同意不下载、安装、重启或升级。

Skill 与桌面端版本号相互独立。基础动作以 `cli status` 和 `cli capabilities` 的当前返回为准；可选扩展
还必须以 `cli access list` 的当前访问状态为准。动作契约未列出、访问状态不是 `effective: true`，或命令
报告不支持时停止该调用，不猜参数、不声称功能已存在。

## 低版本桌面端兼容

最新 Skill 可以配合较早的小助手完成该版本已经声明的基础任务，但不能把最新文档中的命令、流程语法或
扩展能力当成旧版已经具备。逐个执行只读探测并分别记录结果；一个查询命令不存在，不代表其他查询或基础
屏幕动作也不存在：

- **基础屏幕任务**：只有 `status`、`capabilities` 和任务所需动作均成功声明时才继续；未列出的命令或
  参数不调用，也不改用其他输入工具绕过小助手。
- **流程创建或修改**：除动作探测外，还必须让当前桌面端返回 `cli workflow schema`，并用同一桌面端
  执行 `workflow validate`。无法取得当前流程语言契约时，可以运行该版本已安装且健康检查通过的流程，
  但停止创建、升级或修复流程，不能凭最新版标准生成后尝试安装。
- **可选扩展**：`access list`、组件状态或 Agent Provider 探测无法执行时，将状态记为“无法确认”；不进入
  不存在的设置入口，不把未授权、未安装、平台不支持和版本过旧混成同一种故障。

`describe`、`access list`、`workflow schema` 和具体动作都要独立容错。旧版不支持某项能力时，向用户说明
“当前桌面版本仍可使用哪些基础能力、哪项任务暂不能安全执行”；只有用户询问或任务确实需要时才提供官方
下载地址，由用户决定是否升级。不得自动下载、安装、重启或中断正在运行的小助手。

## 完成当前任务

1. 用 `cli window list-visible` 或 `cli window wait-selection` 确认目标窗口；有多个候选时让用户选择。
2. 用 `cli task begin` 绑定目标；绑定后先检查目标进程是否为当前支持的浏览器，再用 `cli task observe` 获取当前可见状态。
3. 若 Windows 目标为 Chrome/Edge，或 macOS 目标为 Chrome，且浏览器增强动作契约与访问状态均有效，先向用户推荐浏览器增强。优先继续使用当前窗口或已由小助手管理的浏览器会话；普通屏幕能力足以完成任务时，不得仅为使用 DOM 而要求用户切换窗口。只有任务确实需要完整页面结构化读取、选择或复制，且当前窗口无法安全接管时，才进入重开流程。
4. 用户说“这篇文章”或“当前页面”但未给 URL，且当前窗口无法接管时，先取得用户同意，再从已确认浏览器地址栏临时读取当前 `http/https` URL：保存原剪贴板，地址栏全选复制，校验 URL，退出地址栏并立即恢复原剪贴板；URL 只保留在当前任务内，不写日志或结果。无法取得合法 URL 时先请用户提供链接，不能让用户关闭后再丢失页面。确需关闭重开时只给简短提示：`当前浏览器暂时无法直接接管。请先关闭浏览器；关闭后告诉我“已关闭”，我会重新打开当前页面并继续。` 不自行关闭用户浏览器；用户拒绝时继续已授权的普通屏幕操作。
5. 用户要求选择或复制网页正文、列表、链接、表格或跨滚动区域内容时，优先触发上述浏览器增强提示。先检查当前 `cli capabilities` 是否真实列出 `ctx.browser.select_text` / `ctx.browser.copy`：已列出时按流程标准调用；未列出时仅在用户明确要求复制、且流程已声明读取浏览器与写入剪贴板权限时，才可用当前 `ctx.browser.read` 将唯一对象的明确字段写入剪贴板，但不得声称形成了页面可见选区。不要用 `Ctrl+A` 或盲目拖拽冒充。
   “帮我复制一下这篇文章的正文部分”等自然语言直接视为这一意图，不要求用户提供 selector、解释 DOM 或改写成命令。
6. 优先依据当前观察结果定位。坐标只能来自本次有效观察或明确的相对规则，不能沿用旧截图坐标。
7. 每次改变屏幕前确认动作仍在用户授权范围内；关键或不可逆动作在执行前单独确认。
8. 点击、输入、滚动或拖动后重新观察并验证可见结果。命令成功只证明事件已发送。
9. 完成、失败或用户停止时执行 `cli task end`，报告结果、未完成项和保存位置。

常用原生命令形态：

```text
cli task begin [--handle <窗口句柄>]
cli task observe
cli task find --text <文字>
cli task wait --text <文字> --timeout <秒> --interval <秒>
cli task click --point <x,y> --button left
cli task write --text <文字> --interval <秒>
cli task scroll --point <x,y> --amount <数值> --direction up|down|left|right
cli task hotkey <按键...>
cli task end
```

跨应用任务可在用户授权范围内直接启动应用，再确认新窗口；启动窗口只是第一个坐标锚点，不是
全程限制：

```text
cli application launch --name "微信"
cli window wait-selection --title "微信" --timeout 30
cli window activate --target <target_id>
cli window arrange --handles <handle1> <handle2> --layout columns
```

调用前必须确认 `cli capabilities` 列出 `application.launch` 和任务所需窗口动作。流程语言中优先
使用 `应用`、`找不到时：启动应用`、`打开应用【名称】`、新窗口登记和命名操作区域；执行到哪个
操作区域，底座就激活其绑定窗口。窗口允许重叠，也可排列，不得把启动窗口误解为全流程排他锁。
`应用` 直接写为 Windows `.exe` 文件名且没有另写 `首选进程` 时，该文件名是严格进程条件；不得用
标题相同的其他应用窗口代替。纯浏览器增强步骤可以省略 `在`，因为它操作受管会话对象；普通
Chrome/Edge 窗口即使标题相同，也不能被当作已经打开的受管浏览器会话。
流程主动打开并登记的新应用窗口默认继承启动窗口的位置和大小；受管浏览器窗口创建后也由底座
强制应用该区域。只有流程显式排列窗口或指定其他布局时，才覆盖这个默认摆放。
`打开浏览器会话` 步骤中的浏览器元素观察由底座延后到会话创建后作为就绪检查；不得在会话尚未
创建时先调用 `browser locate`。纯浏览器观察/验证步骤同样不要求桌面操作区域。
网页可见文字条件使用 `浏览器出现文字【文字】`，不要把普通文字写进 `浏览器出现元素【CSS selector】`。
登录或验证需要用户操作时使用 `失败：等待用户继续`；底座暂停并显示等待状态，用户点击主界面现有
“继续”按钮后立即复检，未满足则再次等待。
需要自动检测时使用 `失败：等待用户继续；10秒重试`；底座每 10 秒自动复检，用户点击“继续”可
提前唤醒。所有普通页面文字条件都必须使用文字语法，不能写进元素 selector。

浏览器增强提供独立的顶层 CLI，适合 Agent 完成一次性网页任务；命令和参数必须以当前
`browser --help` 与能力返回为准：

```text
browser status
browser open chrome|edge [--url <http/https URL>]
browser navigate --browser chrome|edge <http/https URL>
browser auth-status --browser chrome|edge
browser locate --browser chrome|edge [--selector <CSS>] [--match-text <文字>] [--limit <数量>]
browser read|click|fill|select-text|copy|scroll|press|verify|download --browser chrome|edge ...
browser close chrome|edge
```

同一网页任务只在首次需要受管浏览器时执行一次 `browser open`，后续每一轮观察、操作和验证即使由
不同 CLI 进程执行，也必须通过同一个 `--browser chrome|edge` 复用该受管会话。不得把步骤包装成
`open → navigate/read/locate → close`，不得在每轮决策前再次 `open`，也不得由 Agent 自行使用
`browser open --new`。只有收到 `browser_session_expired` 时才允许重新 `open` 一次；收到
`browser_session_not_open` 时先执行 `browser status` 并报告状态，禁止无限重试。任务完成、失败或用户
停止时再执行一次 `browser close chrome|edge`；除非用户明确要求结束整个浏览器增强服务，否则不加
`--stop-daemon`。

用户给出网址时直接执行一次 `browser open chrome|edge --url <网址>`，让小助手创建或复用受管会话并
进入页面。若结果为 `status=waiting_for_user`、`reason=login_required` 且用户没有提供凭据，立即停止网页
工具调用，保持当前窗口和页面不动并请用户完成登录或验证；不得刷新、关闭或重开。用户明确提供账号、密码或验证码时允许
小助手代填，但敏感文字必须通过工具的非回显输入通道，仅用于本次指定操作，不得写入命令行、流程文件、
日志或结果。用户确认完成后执行
`browser auth-status --browser chrome|edge`，仅在返回 `status=ready` 后继续使用原会话。受管浏览器的
持久化 Profile 会跨正常关闭和小助手重启保留网站登录状态；网站仍可主动使登录过期。只禁止 Agent 将
Cookie、密码等原始凭据写入模型上下文、流程文件、运行日志或结果输出。

`locate` 可用 `--limit` 限制候选数量；后续读取或操作在未提供已定位对象时必须匹配唯一目标，相关命令
明确支持 `--index` 时才可从多个候选中选择。`verify` 接受动作与期望 JSON。
浏览器组件低于 `0.1.3` 且返回 `browser_component_update_required` 时停止，请用户在“设置 → 组件”自行更新，
不得绕过版本检查或直接启动 Sidecar。

具体参数仍以 `cli capabilities` 为准。横向滚动必须使用 `--direction left|right`，不得以
`Shift+滚轮` 假冒。事件发送后若画面未变化，按 `no_change` 处理。

## 可选能力

浏览器增强、Agent 接入和 VLM 屏幕理解均可能需要单独组件或能力码。能力缺失、未授权或需要激活时停止，
由用户联系开发者购买并自行激活；不得猜测、索取、记录、代输或绕过能力码。浏览器增强不是独立执行者；
用户当前普通浏览器可由屏幕/UIA可靠完成时直接继续，需要 DOM 时复用小助手的持久化受管 Profile。

浏览器增强启动的是正常浏览器窗口，必须保留地址栏，供用户确认当前网址、登录状态和页面范围；只有“帮助中心”信息窗口可以使用无地址栏的应用窗口。若浏览器增强窗口没有地址栏，停止操作并报告启动配置异常。

浏览器增强开始前必须同时满足两项：`cli capabilities` 列出 `workflow.browser-enhancement@1`，且
`cli access list` 中 `browser_enhancement.status.effective` 为 `true`。前者证明当前桌面版本公开了
`ctx.browser` 动作契约，后者同时核对授权、组件安装、平台可用性和启用状态。只满足其中一项不能运行。
若旧版 `cli capabilities` 未列出该动作，即使设置页显示已购买或已安装也停止，并说明需要用户自行决定
是否升级桌面端；若动作已列出但访问状态无效，按返回的 `reason` 和 `action` 区分未授权、未安装、不可用
或未启用，不把这些状态统称为“缺少能力码”。

开发、修改或验收浏览器增强流程时，还必须完整读取
[浏览器增强测试标准](references/browser-enhancement-testing.md)，按任务涉及的层级记录实际执行、跳过项和
证据；静态校验、隔离 Sidecar、正式在线组件和真实业务页面是不同验收层，不能互相代替。

任务涉及 `执行者：agent`、Agent Bridge、Provider、DSH、VLM、截图外发或 Agent 接入诊断时，必须先
完整读取 [Agent 接入与视觉模型标准](references/agent-bridge.md)。创建、修改或修复流程前，必须完整
读取 [流程开发标准](references/workflow-standard.md)，并使用本目录 `scripts/workflow_dev.ps1` 或
`scripts/workflow_dev.sh` 定位 CLI 和执行标准中明确列出的兼容桥接动作。不得凭示例或旧对话补写规则。

只读诊断 Agent Bridge 时优先使用 `agent status`；需要实际探测当前已配置 Provider 时使用
`agent probe`。这两个命令不配置、不启用 Provider，也不接收 Token。`runs pending-agent`、
`runs agent-context/claim/complete/fail` 属于外部 Agent 主动领取 checkpoint 的另一条路径，不能混用。

流程工程坚持“确认窗口—只读识别—页面判断—模拟运行—监督操作—失败恢复—小批量”的逐级验收；
流程语言 v2 中的变量、条件、有界循环、有界重试、验证和人工确认优先于原子动作堆叠。每个改变页面
的动作都必须有操作前观察和操作后验证，权限保持最低必要，第三方流程不得冒充目标平台官方能力。

## 安全边界

- 用户有权执行并明确要求的日常操作都可编写为流程，不因包含登录、账号操作、发布、删除或支付步骤而一概拒绝。Agent 可执行用户授权的正常操作；只禁止 Agent 将 Cookie、密码等原始凭据写入模型上下文、流程文件、运行日志或结果输出；技术上无法代办的扫码、安全密钥、生物识别才等待用户。
- 截图或屏幕内容发送到外部模型前，明确 Provider、范围和用途并取得确认；避开无关隐私。
- 以用户当前任务为操作授权，可直接使用任务所需的浏览器页面和本机窗口；Cookie、密码等原始凭据不得写入模型上下文、流程文件、运行日志或结果输出；不用技术成功替代业务结果验证。
- 用户说暂停、停止或取消时立即停止后续操作。
