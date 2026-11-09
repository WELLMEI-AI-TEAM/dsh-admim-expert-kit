# 行政管理专家套件（Admin Expert Kit）· v0.1.0

> **包级汇总文件：请不要把本文件单独放进技能目录。** 正确装法：把 `skills\` 下 5 个技能目录（连同各自文件夹）拷入你自己的 DSH 技能目录——Windows 为 `C:\Users\<用户名>\.dsh\skills\`，Mac/Linux 为 `~/.dsh/skills/`；新开一个会话即生效。详见包内 INSTALL.md。

```
---
name: admin-expert-kit
description: "行政管理专家套件（5 技能包）：通知公文、会议纪要、接待与行程、办公用品与固定资产台账、活动策划，把一句话事项变成原生可编辑的 Word/Excel 成品。"
metadata:
  slug: "admin-expert-kit"
  displayName: "行政管理专家"
  version: "0.1.0"
  summary: "行政/综合管理岗能力套件：5 技能 + 连接器增强 + 套件页（MANIFEST.md）"
---
```

## 包含技能（frontmatter 汇总）

| slug | 显示名 | 版本 | 一句话能力 | 触发词示例 | 成品 |
| --- | --- | --- | --- | --- | --- |
| admin-notice-docs | 通知公文 | 0.1.0 | 一句话事项→规范排版的 Word 通知/请示/通报/函/启事 | 写个通知、拟个通告、发公文、关于某某的通知 | .docx |
| admin-meeting-minutes | 会议纪要 | 0.1.0 | 散记/转写→规范纪要＋决议跟进台账 | 整理会议纪要、会后记录、决议跟进 | .docx + .xlsx |
| admin-reception-travel | 接待与行程 | 0.1.0 | 来访信息→分级接待方案＋逐时刻行程表（冲突校验） | 来访接待、安排考察、客户到访、做个行程表 | .docx + .xlsx |
| admin-asset-ledger | 办公用品与固定资产台账 | 0.1.0 | 带公式与低耗红警的台账＋出入库盘点流程 | 建个台账、办公用品登记、固定资产盘点、领用表 | .xlsx |
| admin-event-planning | 活动策划 | 0.1.0 | 一句话目的→九节方案书＋预算/RACI＋倒排计划 | 年会、团建、开业、发布会、方案、预算 | .docx + .xlsx |

每个技能的完整方法论与模板在 `skills\<slug>\SKILL.md` 与 `references\` 细则里（各目录 3 个文件）。

## 套件门面与实证

- 套件页（说明/适用角色/快捷指令/Skills/Connectors/使用边界/持续维护七节）：见包内 **MANIFEST.md**
- 安装与验收：见包内 **INSTALL.md**
- 连接器（可选增强）：不连任何连接器也能出全部成品；推荐连接器清单（钉钉零凭据可用等 17 个实证）见 MANIFEST.md 第五节
- 本包不含密钥/凭据/外部账号配置；模板中电话、证照、金额一律为【待确认】占位

**版本**：2026-11-02 · 维护：DSH 套件开发专家 Bot（用户委托）
