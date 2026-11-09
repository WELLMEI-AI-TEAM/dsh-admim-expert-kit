# 本地结构化检查接口

脚本只读UTF-8 JSON，不联网、不修改输入、不启动Office、不代替原始材料核对。要求Python 3.9+标准库，无pip依赖；数字推荐用十进制字符串，拒绝负数量、NaN、Infinity和布尔数字。

```text
python "<本技能目录>/scripts/check.py" "<本技能目录>/references/example.json"
```

示例数据全为虚构，见 [example.json](example.json)，请复制到用户输出目录修改，不改技能内样例。

period_start/period_end为含首尾日区间；items含唯一id、unit、opening、safety，可选actual；movements含唯一id、date、item_id、direction（入/领/退/损）、正quantity、同一unit，unit_price可空。退库按提供的原领用价；缺价返回金额null，不默认为0。脚本只核期末数量、净耗用、发生时金额、盘点差异与补货建议，不核资产折旧、日内库存、审批或单据真实性。未盘actual为null，不是已盘点一致；盘点任务设置顶层stocktake=true，缺实盘会返回needs_review。

输出JSON含status、issues（status/code/ref/message）、computed与scope。`passed`/退出0只表示显式结构化字段满足本脚本检查；`needs_review`/退出2表示缺项、预警或待人工核实；`failed`/退出1表示输入无效或规则冲突。原文真实性、Excel公式重算、Word分页均需另验。

输入错误也输出JSON并退出1；无数据不会显示全部通过。用户仅要正文时不必为了跑脚本强制创建JSON。
