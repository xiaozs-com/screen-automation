# 屏幕自动化工程师 WorkBuddy Expert

本专家在 WorkBuddy 中帮助用户理解和控制屏幕，并通过自然语言创建、维护自动化流程。
屏幕自动化小助手桌面端提供 Windows 与 macOS 的本地识别、控制和流程执行能力。
基础任务可直接使用；小助手桌面端配置好“Agent接入”后，流程可调用 Provider 实现智能定位、智能执行与智能异常处理。
账号授权、支付及其他高风险操作由用户在场亲自完成。

它预加载 `screen-automation` 原子 Skill；内嵌 Skill 副本由仓库根目录
`tools/assemble_assets.py --sync` 从 `skills/screen-automation/` 确定性同步，不应手工修改。

本地验证与打包使用 `tools/assemble_assets.py --check --build`。生成 ZIP 仅用于本地验收；发布到 WorkBuddy
开放平台必须另行取得明确授权。
