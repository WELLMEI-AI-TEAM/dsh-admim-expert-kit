# 行政管理专家 · 专家套件（Expert Kit）

| 项 | 值 |
| --- | --- |
| 套件名 | **行政管理专家**（Admin Expert Kit） |
| 岗位分类 | 行政 / 综合管理（对标千问办公按岗位成套：产品设计、企业财税、合同管理等） |
| 版本 | 套件 v0.1.0 · 文档层 v0.1.1（2026-11-02） |
| 载体 | Skills＝SkillHub 形态 SKILL.md 文件技能（`.dsh\skills\`）；Connectors＝能力 `admin-kit-connectors`；编组＝capability pack `admin-expert-kit`；整套索引＝本文件 |
| 对千问差异化 | 支持个人产出上传公开市场（SkillHub）；成品直落 Word/Excel 原生可编辑；连接器不内置凭据 |

## 一、套件说明

「行政管理专家」是面向行政 / 综合管理岗位的一组专业能力套件：5 个岗位技能覆盖通知公文、会议纪要、接待与行程、办公用品与固定资产台账、活动策划五个日常场景，配合 DSH 连接器货架的办公协作增强，把一句话事项直接变成可编辑的 Word/Excel 正式成品。所有技能为完整 SOP（方法论＋模板＋检查清单），非提示词片段；连接器与配套插件全部实证，无一编造。

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

## 四、Skills（5 个核心技能，单一真源 = `.dsh\skills\`）

每技能 = SKILL.md（frontmatter 与 dev-god 同构：`name/description/metadata{slug,displayName,version,summary}`）＋ `references/` 两份分场景细则。SOP 一句话：

| 技能 | 方法论一句话 | 输出规范 |
| --- | --- | --- |
| admin-notice-docs 通知公文 | 五文种、一文一事、标题=机关+事由+文种；信息采集表缺项必问，电话绝不编造留【联系电话】 | Word 原生可编辑，GB/T 9704 风格排版 |
| admin-meeting-minutes 会议纪要 | 四层速记法；行动项五要素＝事项/负责人/协助方/完成时限/验收标准 | 纪要 Word ＋ 决议台账 Excel（状态下拉、延期红警条件格式） |
| admin-reception-travel 接待与行程 | 信息确认清单（禁忌/涉密标【待确认】）→分级接待分组→逐时刻行程；缓冲：楼宇间≥15min、高铁+30min、机场+60min，送站反推 | 方案 Word ＋ 行程 Excel（冲突校验 6 条） |
| admin-asset-ledger 台账 | 结存=期初+入库−领用；编号 XS-/GD-部门码-年份-流水；月折旧公式；补货=安全库存×2−结存 | Excel 公式原生（非死数）、低耗整行红警 |
| admin-event-planning 活动策划 | 需求七问→九节方案书→倒排计划→预算（备用金=总额8%）＋RACI（每任务唯一 A） | 方案 Word ＋ 预算/分工 Excel（改数全表联动） |

公共输出规范：Word/WPS 现场打开可改（office 工具实时写入渲染复核）；Excel 公式列非死数；字体缺失走技能自带降级表。

## 五、Connectors（可选增强）

**5 个技能出成品不依赖任何连接器**；连接器只负责"把成品和数据进企业系统"。2026-11-02 货架「办公协作」类 17 个在架实证，行政岗推荐：

| 连接器 | 鉴权 | 行政用途 |
| --- | --- | --- |
| dingtalk 钉钉工作台 | none（**零凭据可现场演示**） | 通讯录/日历/待办/OA审批只读 |
| feishu 飞书开放平台 | api-key | 消息/文档/多维表格（纪要回填） |
| wecom 企业微信（社区） | api-key | 通讯录/消息/企业协作 |
| m365 Microsoft 365 | api-key | Outlook 邮件/日历/Teams |
| google-calendar | api-key | 行程表事件写入 |
| netease-mail / qq-mail（社区） | api-key | 邮件起草发送 |
| jinshuju-forms | oauth2-pkce | 活动报名表单收集 |

规则：连接一律走宿主连接器体系（货架安装/授权）；凭据一律 `request_secret` 安全卡，不落套件文件、不上聊天；只读数据仅用于填充模板；一切对外发送先向用户复述收件人与内容再执行。编组载体已注册：能力 `admin-kit-connectors` ＋ pack `admin-expert-kit`（2026-11-02 实测 pack 收不进文件技能、只编组 capability，故完整编组道具为本文件）。

## 六、使用边界

- **可编辑边界**（DSH 版「个人编辑仅本地生效」口径）：文件技能在 `C:\Users\Administrator\.dsh\skills\admin-*\`，个人改动仅本机生效；套件更新**不会自动覆盖本地修改**——更新只替换工作区源文件，拷入 skills 目录是显式动作，拷前手动 diff 自己的改动（对应千问"更新覆盖本地修改有提示"）。
- **数据边界**：电话/证照号/金额费用一律不编造，缺项留【待确认】占位；演示数据全虚构；涉密材料不进套件模板与连接器演示。
- **能力边界**：公文排版为 GB/T 9704 风格**降级复刻**（正式红头、发文字号走机关正式模板流程）；语音播报、微信桥等为配套插件能力（附录 A），不在套件本体。
- **执行边界**：本机沙箱内终端进程受限，终端命令需用户逐次批准（2026-11-02 实测记录）；文件与 Office 工具操作不受影响。

## 七、持续维护

**版本记录**
- v0.1.0（2026-11-02）：首个版本。5 技能（15 文件）全部含 SOP＋模板＋检查清单；连接器与插件清单实证；早会演示脚本就绪。
- v0.1.1（2026-11-02，仅文档层）：套件页按千问「专家套件」格式重排（说明/角色/快捷指令/Skills/Connectors/边界/维护七节）；5 个技能本体未动。
- **装机状态（2026-11-02）**：本机安装完成（Chief ②留痕：查重无冲突、只增未改、各目录 3 文件、frontmatter 直读核验；宿主无需重启即感知）。

**更新方式**：工作区源目录修改 → 与本文件版本记录比对 → 显式拷入 `.dsh\skills\`。
**v0.2 计划**：SkillHub 逐技能上架（公开分发＝用户终批档）、钉钉/飞书按企业接入示例、pack 可携带性随宿主机制演进。
**维护人**：DSH 套件开发专家 Bot（用户委托，Chief 监督）。**验收**：见 INSTALL-AND-DEMO.md「验收三步」（结构/触发/成品）。

## 附录 A：配套插件（8 个，包名全部实证）

来源：官方目录（数据截止 2026-10-27）＋ npm 实时核验（2026-11-02，工具实测），全部存在：

| 包名 | 版本 | 健康度 | 行政岗用途 | 建议 |
| --- | --- | --- | --- | --- |
| dsh-work-assistant | 0.5.6 | 59 | 微信机器人通道、工作账本、知识库、定时提醒 | 推荐 |
| dsh-mishu | 0.6.2 | 59 | 账单/续费/证件到期等「dated things」盯办 | 推荐 |
| dsh-msg-hub | 0.1.11 | 71 | 微信/QQ/飞书消息桥+主动推送 | 推荐 |
| dsh-feishu-board | 0.2.3 | 59 | 各会话提问推飞书私聊、回复回填 | 按需 |
| @zzerx/dsh-plugin-notes | 0.6.0 | 76 | 便签变任务：泳道、定时跑、WebDAV备份 | 推荐 |
| dsh-speak | 1.8.4 | 75 | 语音播报（会议提醒/结果播报，演示加分） | 推荐 |
| dsh-float | 0.1.0 | 47 | 桌面悬浮助手面板（新包、下载量低） | 尝鲜可选 |
| dsh-tylina | 0.15.2 | 73 | wasm 运行时依赖包（某些插件的底座） | 随依赖装 |

## 附录 B：目录结构与卸载

```
admin-expert-kit/
├─ MANIFEST.md            ← 本文件（套件页 + 版本记录）
├─ INSTALL-AND-DEMO.md    ← 安装使用一页说明 + 早会演示脚本
└─ skills/
   ├─ admin-notice-docs/        SKILL.md + references/{notice-templates,format-spec}.md
   ├─ admin-meeting-minutes/    SKILL.md + references/{minutes-template,action-tracker}.md
   ├─ admin-reception-travel/   SKILL.md + references/{reception-plan-template,itinerary-template}.md
   ├─ admin-asset-ledger/       SKILL.md + references/{ledger-schema,inout-stocktake}.md
   └─ admin-event-planning/     SKILL.md + references/{event-plan-template,budget-roles}.md
```

已装目录 `C:\Users\Administrator\.dsh\skills\` 下同名 5 目录与本处同构（每目录 3 文件）。**卸载**：删除 skills 目录下对应 5 个目录即可，无残留（不写注册表、不装服务）；`admin-kit-connectors`/`admin-expert-kit` 两个 capability 条目可一并删除。
