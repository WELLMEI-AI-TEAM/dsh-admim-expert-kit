#!/usr/bin/env python3
"""Local, read-only structured checks. Python 3.9+, no third-party dependencies."""
import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


def number(value, field, minimum=Decimal("0")):
    if isinstance(value, bool) or value is None:
        raise ValueError(field + ": expected a finite number")
    result = Decimal(str(value))
    if not result.is_finite() or (minimum is not None and result < minimum):
        raise ValueError(field + ": number outside allowed range")
    return result


def missing(value):
    return value is None or (isinstance(value, str) and (not value.strip() or "待确认" in value or "待补" in value))


def rows(data, key):
    value = data.get(key)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError(key + ": expected an array of objects")
    return value


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + ": expected nonempty text")
    return value.strip()


def day(value):
    value = text(value, "date")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("date: expected YYYY-MM-DD")
    return date.fromisoformat(value)


def stamp(value):
    result = datetime.fromisoformat(text(value, "timestamp").replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamp: include explicit timezone offset, e.g. +08:00")
    return result.astimezone(timezone.utc)


def validate(data):
    issues = []
    computed = {}
    def issue(status, code, ref, message):
        issues.append({"status": status, "code": code, "ref": str(ref), "message": message})
    try:
        if not isinstance(data, dict):
            raise ValueError("input: expected a JSON object")
        inspect(data, issue, computed)
    except (ValueError, TypeError, KeyError, InvalidOperation, OverflowError) as exc:
        issue("failed", "invalid_input", "input", str(exc))
    status = "failed" if any(x["status"] == "failed" for x in issues) else "needs_review" if issues else "passed"
    return {"status": status, "issues": issues, "computed": computed,
            "scope": "Structured fields only; source truth, spreadsheet recalculation and visual rendering are not verified."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON input; never modified")
    args = parser.parse_args()
    try:
        report = validate(json.loads(args.input.read_text(encoding="utf-8-sig")))
    except (OSError, ValueError) as exc:
        report = {"status": "failed", "issues": [{"status": "failed", "code": "input_read_error", "ref": "input", "message": str(exc)}], "computed": {}}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return {"passed": 0, "failed": 1, "needs_review": 2}[report["status"]]


def inspect(data, issue, computed):
    start, end = day(data.get("period_start")), day(data.get("period_end"))
    if end < start:
        raise ValueError("period_end must not precede period_start")
    items, movements = rows(data, "items"), rows(data, "movements")
    if not items:
        issue("needs_review", "empty_items", "items", "No inventory master data to reconcile.")
    master, balance, usage, seen, usage_amount = {}, {}, {}, set(), {}
    for row in items:
        key = text(row.get("id"), "items.id")
        if key in master:
            raise ValueError("duplicate item ID: " + key)
        master[key] = row
        text(row.get("unit"), "items.unit")
        balance[key] = number(row.get("opening"), key + ".opening")
        usage[key], usage_amount[key] = Decimal(0), Decimal(0)
        number(row.get("safety"), key + ".safety")
    dated = []
    for row in movements:
        key = text(row.get("id"), "movements.id")
        if key in seen:
            issue("failed", "duplicate_movement", key, "Duplicate movement must not be counted twice.")
            continue
        seen.add(key)
        item = text(row.get("item_id"), "item_id")
        if item not in master:
            issue("failed", "unknown_item", key, "Movement references an unknown inventory item.")
            continue
        value = number(row.get("quantity"), key + ".quantity")
        if value == 0:
            raise ValueError(key + ": quantity must be positive")
        direction = row.get("direction")
        if direction not in ("入", "领", "退", "损"):
            raise ValueError(key + ": direction must be 入/领/退/损")
        if row.get("unit") != master[item]["unit"]:
            issue("failed", "unit_mismatch", key, "Convert units before aggregating inventory.")
            continue
        at = day(row.get("date"))
        if not start <= at <= end:
            continue
        dated.append((at, key, row, item, value, direction))
    for at, key, row, item, value, direction in sorted(dated, key=lambda x: (x[0], x[1])):
        # Same-day input order is not a timestamp: only period-end balance is checked.
        balance[item] += value if direction in ("入", "退") else -value
        if direction in ("领", "退"):
            sign = 1 if direction == "领" else -1
            usage[item] += sign * value
            if missing(row.get("unit_price")):
                usage_amount[item] = None
                issue("needs_review", "missing_price", key, "Historical consumption amount is unknown without a movement price.")
            else:
                amount = (number(row["unit_price"], key + ".unit_price") * value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                if usage_amount[item] is not None:
                    usage_amount[item] += sign * amount
    results = []
    for key, row in master.items():
        stock, safety = balance[key], number(row["safety"], key + ".safety")
        if stock < 0:
            issue("failed", "negative_stock", key, "Period-end stock is negative; investigate source movements.")
        if stock < safety:
            issue("needs_review", "low_stock", key, "Stock is below the safety level.")
        actual = row.get("actual")
        if data.get("stocktake") is True and missing(actual):
            issue("needs_review", "not_counted", key, "No physical count was supplied for stocktake.")
        difference = None if missing(actual) else number(actual, key + ".actual") - stock
        if difference is not None and difference != 0:
            issue("needs_review", "stocktake_difference", key, "Actual minus book stock is nonzero; approval is needed before adjustment.")
        results.append({"id": key, "closing": str(stock), "net_usage": str(usage[key]),
                        "usage_amount": str(usage_amount[key]) if usage_amount[key] is not None else None,
                        "stocktake_difference": str(difference) if difference is not None else None,
                        "reorder": str(max(Decimal(0), safety * 2 - stock))})
    computed["items"] = results


if __name__ == "__main__":
    sys.exit(main())
