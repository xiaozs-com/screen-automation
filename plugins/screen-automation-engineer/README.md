# 屏幕自动化工程师 WorkBuddy Expert

本目录是“屏幕自动化工程师”WorkBuddy Expert 的源码资产：基于“屏幕自动化小助手”这一**本地屏幕自动化基础平台**，安全完成当前屏幕任务，并把重复任务沉淀为可维护流程。它预加载 `screen-automation` 原子 Skill；内嵌 Skill 副本由仓库根目录
`tools/assemble_assets.py --sync` 从 `skills/screen-automation/` 确定性同步，不应手工修改。

本地验证与打包使用 `tools/assemble_assets.py --check --build`。生成 ZIP 仅用于本地验收；发布到 WorkBuddy
开放平台必须另行取得明确授权。
