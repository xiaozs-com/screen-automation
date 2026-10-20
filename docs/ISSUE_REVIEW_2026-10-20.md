# 1.2.5 问题清单核验

核验对象：用户提供的《屏幕自动化工程师-1.2.5-问题清单.md》。

| 项目 | 结论与处理 |
| --- | --- |
| 1. PowerShell 5.1 入口编码 | 确认。resolve_cli.ps1 增加 UTF-8 BOM；装配器拒绝无 BOM 的非 ASCII PowerShell 脚本，ASCII 脚本允许无 BOM。Windows PowerShell 5.1 实际解析与执行通过。 |
| 2. inspect / validate 混用 | 确认。入口、开发标准和阶段参考统一为本地源路径 inspect，安装后按流程标识 validate。 |
| 3. Bash 入口平台提示 | 确认。文档明确 macOS；脚本在非 Darwin 系统直接提示使用 Windows PowerShell 入口。Git Bash 实测拒绝码为 2。 |
| 4. 新旧能力描述混淆 | 当前桌面源码已在 SDK 描述标明语言 2 兼容与语言 3 阶段区别，不重复改动。清单中的运行安装包不能据此视为已更新。 |
| 5. inspect 缺语言版本 | 确认。桌面 workflows/manager.py 新增 language_version 与 required_capabilities；保持原 format 字段，Python 等非 Markdown 格式的语言版本为 null。 |
| 6. --help 报异常 | 确认。桌面 runtime/main.py 将 SystemExit(0/None) 作为正常退出，不打印异常；非零退出与用户停止处理保持原行为。 |
| 7. 空行与前提重复 | 确认。清理生命周期连续空行；操作参考仅保留浏览器特有条件，通用前提引用 Skill 主入口。 |
| 安装侧旧缓存 | 不属于源码包问题。未删除、升级或改动用户的已安装副本或缓存。 |

验证：资产编码回归 2 项通过；桌面 CLI、真实入口 help、inspect 语言字段、流程编译、运行分派与停止相关回归 124 项通过。
桌面端两处实现和新增测试位于 screen-automation-helper 独立仓库，保留其中已有未提交修改。
测试针对当前工作区；未构建桌面安装包，已安装程序需另行交付才能包含桌面端修复。
四类 Skill/专家包重新生成；版本保持 1.2.5。未提交、推送或发布市场。
