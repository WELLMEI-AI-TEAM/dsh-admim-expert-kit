# DSH 行政管理专家套件 · v0.2.0

5 个可独立使用的文件技能，覆盖通知公文、会议纪要、接待行程、资产台账和活动策划。保留 DSH `metadata` 字段与原技能名；本版增加业务检查脚本、输入样例和按任务裁剪的交付流程。

| 技能 | 示例请求 | 本版重点 |
| --- | --- | --- |
| [通知公文](skills/admin-notice-docs/SKILL.md) | 写消防演练通知；只改这份通知的日期 | 文种与改稿分流、事实来源、日期/星期检查 |
| [会议纪要](skills/admin-meeting-minutes/SKILL.md) | 整理会议笔记并更新行动项 | 建议与决议分离、来源定位、缺期限与取消项处理 |
| [接待与行程](skills/admin-reception-travel/SKILL.md) | 排客户来访和送站行程 | 跨日时区、共享资源冲突、送站反推 |
| [资产台账](skills/admin-asset-ledger/SKILL.md) | 做办公用品出入库与盘点表 | 退库/报损、历史价格、盘点差异方向与缺价 |
| [活动策划](skills/admin-event-planning/SKILL.md) | 做团建方案、预算和分工 | 备用金两种基数、预算上限、RACI与依赖检查 |

## 使用与安装

将 `skills/` 中需要的整个技能文件夹拷入 DSH 技能目录（Windows通常为 `%USERPROFILE%\.dsh\skills\`）。已有同名技能时先备份并比对个人修改，再替换；在新会话核对是否加载。仓库更新不会自动修改运行中的 DSH 配置。

单独上传市场用 [dist/upload/](dist/upload/) 下的 `dsh-admin-*-v0.2.0.zip`，每包根目录有一个 `SKILL.md`，包含本技能引用的资料、脚本和许可证。新包尚未实际上传/导入市场；历史 v0.1.x 包保留，当前入口见 [dist/README.md](dist/README.md)。

脚本只需 Python 3.9+ 标准库，不联网、不改输入、不依赖其他技能：

```text
python skills/admin-asset-ledger/scripts/check.py skills/admin-asset-ledger/references/example.json
python -B -m unittest discover -s tests -v
python -B tools/build_release.py
```

输出 `passed`/退出0、`failed`/退出1、`needs_review`/退出2。通过只表示输入字段满足脚本规则，不能代表原文事实、Office渲染或Excel计算已经验证。文件生成需宿主可用文档工具或已安装的 python-docx/openpyxl；没有工具仍可先交付正文或表格。

## 对标与验证

对标2026-11-09实测 SkillHub 总榜和办公效率分类下载榜，详见 [BENCHMARK.md](BENCHMARK.md) 和 [排名数据](docs/market-snapshot-2026-11-09.json)。借鉴任务路由、按需资料、可运行脚本、可核验交付；没有复制第三方技能代码或模板。

验证范围、用例与未验证条件见 [SELFTEST.md](SELFTEST.md)。套件结构见 [MANIFEST.md](MANIFEST.md)，安装与演示见 [INSTALL-AND-DEMO.md](INSTALL-AND-DEMO.md)。许可证沿用仓库 [Apache-2.0](LICENSE)。
