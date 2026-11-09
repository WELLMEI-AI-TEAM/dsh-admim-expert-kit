# 本地结构化检查接口

脚本只读UTF-8 JSON，不联网、不修改输入、不启动Office、不代替原始材料核对。要求Python 3.9+标准库，无pip依赖；数字推荐用十进制字符串，拒绝负数量、NaN、Infinity和布尔数字。

```text
python "<本技能目录>/scripts/check.py" "<本技能目录>/references/example.json"
```

示例数据全为虚构，见 [example.json](example.json)，请复制到用户输出目录修改，不改技能内样例。

segments含唯一id、带时区start/end、location、group、resources字符串数组，kind可取meeting/meal/visit/transfer等；跨地点后段用transfer_minutes给实际转移与缓冲。meal需diet_confirmed=true，visit需guide和permission_confirmed=true。departure可选，含at/group/travel_minutes/security_minutes/buffer_minutes/confirmed。时间输出统一UTC。脚本不验证实时路程、连续驾驶、资源别名或车辆跨场转移可达性。

输出JSON含status、issues（status/code/ref/message）、computed与scope。`passed`/退出0只表示显式结构化字段满足本脚本检查；`needs_review`/退出2表示缺项、预警或待人工核实；`failed`/退出1表示输入无效或规则冲突。原文真实性、Excel公式重算、Word分页均需另验。

输入错误也输出JSON并退出1；无数据不会显示全部通过。用户仅要正文时不必为了跑脚本强制创建JSON。
