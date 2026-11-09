# 行政管理专家 · 专家套件（Expert Kit）

| 项 | 值 |
| --- | --- |
| 套件名 | **行政管理专家**（Admin Expert Kit） |
| 岗位分类 | 行政 / 综合管理 |
| 版本 | v0.1.0（2026-11-02） |
| 载体 | 5 个 SkillHub 形态技能文件夹（`skills/`）＋ 本套件页；拷入技能目录即完成安装 |
| 特点 | 成品直落 Word/Excel 原生可编辑；连接器为可选增强且不内置任何凭据；全部模板占位符防编造 |

## 一、套件说明

「行政管理专家」是面向行政 / 综合管理岗位的一组专业能力套件：5 个岗位技能覆盖通知公文、会议纪要、接待与行程、办公用品与固定资产台账、活动策划五个日常场景，配合 DSH 连接器货架的办公协作增强，把一句话事项直接变成可编辑的 Word/Excel 正式成品。所有技能为完整 SOP（方法论＋模板＋检查清单），非提示词片段；连接器与配套插件清单全部实证，无一编造。

## 二、适用角色

- **行政专员 / 综合事务岗 / 文员**：公文与纪要规范化、台账管理
- **部门行政接口人 / 助理**：来访接待、行程编排、活动通知
- **国企与事业单位行政办**：GB/T 9704 风格公文排版（字体缺失有降级表）
- **中小企业主 / 一人公司**：活动策划与预算 RACI、资产台账自管

行业通用；公文与接待分节尤其贴合有正式行文要求的组织。

## 三、快捷指令（预设任务输入）

触发词取自各技能 frontmatter，整句可直接复制使用：

| 你说 | 唤起技能 | 成品 |
| --- | --- | --- |
| 「写个消防演练通知」/「拟个通告」/「关于某某的通知」 | admin-notice-docs | 通知.docx（标题二号居中、仿宋三号、落款右对齐） |
| 「整理这周例会纪要」/「决议跟进」 | admin-meeting-minutes | 纪要.docx ＋ 决议台账.xlsx |
| 「XX公司4人下周五来访，11:23到南站，要参观产线」 | admin-reception-travel | 接待方案.docx ＋ 逐时刻行程表.xlsx（6 条冲突校验） |
| 「建个台账」/「办公用品登记」/「固定资产盘点」 | admin-asset-ledger | 台账.xlsx（公式＋低耗红警＋月度汇总） |
| 「策划今年团建」/「128人秋季团建，给方案和预算」 | admin-event-planning | 九节方案书.docx ＋ 预算/RACI.xlsx |

技能可串联：活动策划方案里的「发活动通知」自动复用通知公文技能。

## 四、Skills（5 个核心技能）

每技能 = SKILL.md（frontmatter：`name/description/metadata{slug,displayName,version,summary}`）＋ `references/` 两份分场景细则。SOP 一句话：

| 技能 | 方法论一句话 | 输出规范 |
| --- | --- | --- |
| admin-notice-docs 通知公文 | 五文种、一文一事、标题=机关+事由+文种；信息采集表缺项必问，电话绝不编造留【联系电话】 | Word 原生可编辑，GB/T 9704 风格排版 |
| admin-meeting-minutes 会议纪要 | 四层速记法；行动项五要素＝事项/负责人/协助方/完成时限/验收标准 | 纪要 Word ＋ 决议台账 Excel（状态下拉、延期红警条件格式） |
| admin-reception-travel 接待与行程 | 信息确认清单（禁忌/涉密标【待确认】）→分级接待分组→逐时刻行程；缓冲：楼宇间≥15min、高铁+30min、机场+60min，送站反推 | 方案 Word ＋ 行程 Excel（冲突校验 6 条） |
| admin-asset-ledger 台账 | 结存=期初+入库−领用；编号 XS-/GD-部门码-年份-流水；月折旧公式；补货=安全库存×2−结存 | Excel 公式原生（非死数）、低耗整行红警 |
| admin-event-planning 活动策划 | 需求七问→九节方案书→倒排计划→预算（备用金=总额8%）＋RACI（每任务唯一 A） | 方案 Word ＋ 预算/分工 Excel（改数全表联动） |

公共输出规范：Word/WPS 现场打开可改；Excel 公式列非死数；字体缺失走技能自带降级表。

## 五、Connectors（可选增强）

**5 个技能出成品不依赖任何连接器**；连接器只负责"把成品和数据进企业系统"。以 DSH 连接器货架「办公协作」类（2026-11-02 实查 17 个在架）为例，行政岗推荐：

| 连接器 | 鉴权 | 行政用途 |
| --- | --- | --- |
| dingtalk 钉钉工作台 | none（零凭据可用） | 通讯录/日历/待办/OA审批只读 |
| feishu 飞书开放平台 | api-key | 消息/文档/多维表格（纪要回填） |
| wecom 企业微信（社区） | api-key | 通讯录/消息/企业协作 |
| m365 Microsoft 365 | api-key | Outlook 邮件/日历/Teams |
| google-calendar | api-key | 行程表事件写入 |
| netease-mail / qq-mail（社区） | api-key | 邮件起草发送 |
| jinshuju-forms | oauth2-pkce | 活动报名表单收集 |

规则：连接一律走宿主自身的连接器体系；凭据一律走宿主的凭据安全卡（如 DSH `request_secret`），不落套件文件；只读数据仅用于填充模板；一切对外发送先复述收件人与内容再执行。

## 六、使用边界

- **可编辑边界**：技能就是技能目录里的普通文件夹，你可以直接改、改完即生效；升级本套件时**先 diff 你自己的改动**再覆盖——本包不会自动更新，拷入哪个目录由你决定。
- **数据边界**：电话/证照号/金额费用一律不编造，缺项留【待确认】占位；涉密材料请勿粘贴进模板或演示。
- **能力边界**：公文排版为 GB/T 9704 风格**降级复刻**（正式红头、发文字号请走机关正式模板流程）；语音播报、微信桥等为可选插件能力（附录 A），不在套件本体。
- **通用性**：方法论与模板跨宿主通用（任何能加载 SKILL.md 形态技能的客户端均可用）；示例中的 Windows 路径仅为演示。

## 七、持续维护

**版本记录**
- v0.1.0（2026-11-02）：首个对外分发版本。5 技能（15 文件）全部含 SOP＋模板＋检查清单；连接器与插件清单实证；本机实测通过结构/触发/成品三步验收。

**更新方式**：新版本以 zip 分发；替换 `skills\` 下对应目录前请先比对你本地的修改。
**计划**：SkillHub 逐技能上架（slug 全局唯一化后）、按企业接入钉钉/飞书连接器示例。
**维护人**：DSH 套件开发专家 Bot（用户委托）。**验收**：见 INSTALL.md「验收三步」。

## 附录 A：可选配套插件（8 个，包名全部实证存在于 npm）

来源：DSH 官方插件目录（数据截止 2026-10-27）＋ npm 实时核验（2026-11-02），全部存在：

| 包名 | 版本 | 健康度 | 行政岗用途 | 建议 |
| --- | --- | --- | --- | --- |
| dsh-work-assistant | 0.5.6 | 59 | 微信机器人通道、工作账本、知识库、定时提醒 | 推荐 |
| dsh-mishu | 0.6.2 | 59 | 账单/续费/证件到期等「dated things」盯办 | 推荐 |
| dsh-msg-hub | 0.1.11 | 71 | 微信/QQ/飞书消息桥+主动推送 | 推荐 |
| dsh-feishu-board | 0.2.3 | 59 | 各会话提问推飞书私聊、回复回填 | 按需 |
| @zzerx/dsh-plugin-notes | 0.6.0 | 76 | 便签变任务：泳道、定时跑、WebDAV备份 | 推荐 |
| dsh-speak | 1.8.4 | 75 | 语音播报（会议提醒/结果播报） | 推荐 |
| dsh-float | 0.1.0 | 47 | 桌面悬浮助手面板（新包、下载量低） | 尝鲜可选 |
| dsh-tylina | 0.15.2 | 73 | wasm 运行时依赖包（某些插件的底座） | 随依赖装 |

非 DSH 宿主可忽略本附录。

## 附录 B：包内结构与卸载

```
admin-expert-kit-v0.1.0.zip
├─ README.md      ← 包级汇总（5 技能 frontmatter 汇总表；勿放入技能目录）
├─ MANIFEST.md    ← 本文件（套件页）
├─ INSTALL.md     ← 安装与验收一页说明
└─ skills/
   ├─ admin-notice-docs/        SKILL.md + references/{notice-templates,format-spec}.md
   ├─ admin-meeting-minutes/    SKILL.md + references/{minutes-template,action-tracker}.md
   ├─ admin-reception-travel/   SKILL.md + references/{reception-plan-template,itinerary-template}.md
   ├─ admin-asset-ledger/       SKILL.md + references/{ledger-schema,inout-stocktake}.md
   └─ admin-event-planning/     SKILL.md + references/{event-plan-template,budget-roles}.md
```

**卸载**：从技能目录删除对应 5 个目录即可，无残留（不写注册表、不装服务）。
