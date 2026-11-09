# 本地结构化检查接口

脚本只读UTF-8 JSON，不联网、不修改输入、不启动Office、不代替原始材料核对。要求Python 3.9+标准库，无pip依赖；数字推荐用十进制字符串，拒绝负数量、NaN、Infinity和布尔数字。

```text
python "<本技能目录>/scripts/check.py" "<本技能目录>/references/example.json"
```

示例数据全为虚构，见 [example.json](example.json)，请复制到用户输出目录修改，不改技能内样例。

currency为统一币种，ceiling为预算上限；reserve_rate在[0,1)，reserve_basis为base或total。budget含id/unit_price/正quantity/currency/status（待询价/已比价/已锁定/已支付）；金额用Decimal按单行四舍五入到分后相加。缺价只返回已知部分并标amounts_complete=false。tasks含id、非空R数组、恰好1人的A数组、start/end日期、depends_on前置ID数组；按日粒度允许同日交接。已支付纳入committed；不证明付款真实发生。

输出JSON含status、issues（status/code/ref/message）、computed与scope。`passed`/退出0只表示显式结构化字段满足本脚本检查；`needs_review`/退出2表示缺项、预警或待人工核实；`failed`/退出1表示输入无效或规则冲突。原文真实性、Excel公式重算、Word分页均需另验。

输入错误也输出JSON并退出1；无数据不会显示全部通过。用户仅要正文时不必为了跑脚本强制创建JSON。
