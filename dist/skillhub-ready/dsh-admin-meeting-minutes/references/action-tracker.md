# 行动项跟进台账（Excel，bundled Python openpyxl 生成）

## 列结构（Sheet1「行动项台账」）

| 列 | 字段 | 规范 |
| --- | --- | --- |
| A | 编号 | A1、A2…与纪要正文呼应 |
| B | 事项 | 动宾短句 |
| C | 来源会议 | 会议纪要-YYYYMMDD |
| D | 负责人 | 实名 |
| E | 协助方 | 实名/部门，可空 |
| F | 完成时限 | 日期格式 yyyy-mm-dd |
| G | 验收标准 | 一条可核查事实 |
| H | 状态 | 下拉：未开始/进行中/已完成/延期/已取消 |
| I | 进展备注 | |
| J | 销项日期 | |

## 公式与自动化

- 表头上方放汇总区：
  `进行中数量 =COUNTIF(H:H,"进行中")`、`完成率 =COUNTIF(H:H,"已完成")/COUNTA(B5:B100)`（按实际起始行）
- 延期高亮（条件格式）：`=AND($F5<TODAY(),$H5<>"已完成",$H5<>"已取消")` → 整行浅红。
- 数据验证：H 列下拉五项；F 列日期格式校验。
- Sheet2「统计透视」：按负责人 COUNTIFS 未完成数，供周会通报。

## 生成代码要点（不落盘示例时按此写）

```python
# bundled python: openpyxl 3.x
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
# 1) 写表头+样式（表头填充#4472C4白字加粗，冻结首行 ws.freeze_panes="A5"）
# 2) DataValidation(type="list", formula1='"未开始,进行中,已完成,延期,已取消"') 加到 H 列
# 3) FormulaRule 延期条件格式
# 4) 列宽按内容设定；B/G 列 wrap_text=True
```

## 使用节奏

- 每次会后：追加本批行动项，改来源会议日期，不覆盖历史行。
- 周会通报前：刷新一遍状态列，延期项逐条问原因进 I 列。
- 季度归档：已取消与已完成满30天的行剪切到「归档」表，保持主表可一眼看完。
