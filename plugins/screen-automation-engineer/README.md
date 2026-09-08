# 屏幕自动化工程师 WorkBuddy Expert

本目录是“屏幕自动化工程师”WorkBuddy Expert 的源码资产：增强 Agent 的屏幕理解与控制能力，利用本地屏幕视觉技术提升界面识别和定位效率，并通过自然语言创建和维护自动化流程。配合支持 Windows 与 macOS 的“屏幕自动化小助手”，完成流程的安装、运行和结果读取。它预加载 `screen-automation` 原子 Skill；内嵌 Skill 副本由仓库根目录
`tools/assemble_assets.py --sync` 从 `skills/screen-automation/` 确定性同步，不应手工修改。

本地验证与打包使用 `tools/assemble_assets.py --check --build`。生成 ZIP 仅用于本地验收；发布到 WorkBuddy
开放平台必须另行取得明确授权。
