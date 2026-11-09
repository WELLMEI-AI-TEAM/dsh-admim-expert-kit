# 本地结构化检查接口

脚本只读UTF-8 JSON，不联网、不修改输入、不启动Office、不代替原始材料核对。要求Python 3.9+标准库，无pip依赖；数字推荐用十进制字符串，拒绝负数量、NaN、Infinity和布尔数字。

```text
python "<本技能目录>/scripts/check.py" "<本技能目录>/references/example.json"
```

示例数据全为虚构，见 [example.json](example.json)，请复制到用户输出目录修改，不改技能内样例。

fields为sender/recipients/subject字符串；dates为日期对象数组，id唯一，date为YYYY-MM-DD，weekday可省略，0为周一到6为周日；before为earlier/later日期ID数组（允许同日，时刻先后仍需人工核对）。未提供的必需事实标needs_review。

输出JSON含status、issues（status/code/ref/message）、computed与scope。`passed`/退出0只表示显式结构化字段满足本脚本检查；`needs_review`/退出2表示缺项、预警或待人工核实；`failed`/退出1表示输入无效或规则冲突。原文真实性、Excel公式重算、Word分页均需另验。

输入错误也输出JSON并退出1；无数据不会显示全部通过。用户仅要正文时不必为了跑脚本强制创建JSON。
