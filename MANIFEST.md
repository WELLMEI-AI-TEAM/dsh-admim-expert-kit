# 行政管理专家套件

版本：v0.2.0，2026-11-09。载体为5个可独立安装的文件技能，不是包含连接器服务的可执行插件。目标用户为行政、综合事务、文秘与部门助理。

| 技能 | 交付与检查 |
| --- | --- |
| admin-notice-docs | 通知/请示/通报/函/启事，按需Word；日期与星期 |
| admin-meeting-minutes | 纪要与行动项，按需Word/Excel；责任/期限/完成依据 |
| admin-reception-travel | 接待分工与行程，按需Word/Excel；跨日/资源/送站 |
| admin-asset-ledger | 流水、库存、资产与盘点，按需Excel；退库/报损/历史价 |
| admin-event-planning | 方案、议程、预算与分工，按需Word/Excel；备用金/RACI/依赖 |

每技能含 `SKILL.md`、2份业务参考、`references/validation.md`、`references/example.json`、`scripts/check.py`，无跨技能运行依赖。入口保留DSH的 `metadata.slug/displayName/version/summary`；发布版用 `dsh-admin-*` 名称，版本与正文和源技能一致。

## 使用方式

短请求直接给所需正文或表格；完整方案按需交付文件，用户模板优先。未明确事实、价格、责任和期限留待确认，不能为模板补造。脚本只检查显式结构化数据，不联网、不修改输入、不自动发送、预订或采购。

Word/Excel生成依赖宿主实际文档能力或已安装的python-docx/openpyxl。文件读回、实际计算和视觉渲染分别记录；没有渲染器或计算器就说明未验证，不能把脚本通过称Office成品通过。

## 安装、更新与数据

安装见 [INSTALL-AND-DEMO.md](INSTALL-AND-DEMO.md)。更新前备份本机同名技能并比对个人修改；工作区提交不自动覆盖已安装技能。卸载只移除对应技能目录，用户输出文件另外保留。

本套件不包含凭据，不依赖连接器。用户确需把成品发往企业系统时，按宿主真实连接器与既有授权处理；凭据走宿主秘密输入，不写进套件。旧文档中的插件版本、连接器数量与装机状态是历史记录，不能作为本版已验证能力。

## 版本与证据

- v0.1.0/文档v0.1.1：初始5技能、模板与分发材料，原始文件可从Git历史和旧ZIP查看。
- v0.2.0：按当前市场高下载技能对标，5技能任务路由与业务口径修正，5个本地检查脚本与独立分发包。

对标证据见 [BENCHMARK.md](BENCHMARK.md)，验证见 [SELFTEST.md](SELFTEST.md)，当前分发见 [dist/README.md](dist/README.md)。未声称新包已上传市场或已在运行中的宿主加载。
