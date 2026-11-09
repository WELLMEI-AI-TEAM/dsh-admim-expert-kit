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
    lines, tasks = rows(data, "budget"), rows(data, "tasks")
    if not lines:
        issue("needs_review", "empty_budget", "budget", "No cost lines to verify.")
    if not tasks:
        issue("needs_review", "empty_tasks", "tasks", "No responsibilities or dependencies to verify.")
    base, committed, paid, seen, currencies = Decimal(0), Decimal(0), Decimal(0), set(), set()
    for row in lines:
        key = text(row.get("id"), "budget.id")
        if key in seen:
            raise ValueError("duplicate budget ID: " + key)
        seen.add(key)
        currency = text(row.get("currency"), "currency")
        currencies.add(currency)
        price = row.get("unit_price")
        quantity = number(row.get("quantity"), key + ".quantity")
        if quantity == 0:
            raise ValueError(key + ": quantity must be positive")
        state = row.get("status")
        if state not in ("待询价", "已比价", "已锁定", "已支付"):
            raise ValueError(key + ": invalid cost status")
        if missing(price):
            issue("needs_review", "missing_quote", key, "Unknown price is not zero cost.")
            continue
        amount = (number(price, "unit_price") * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        base += amount
        if state in ("已锁定", "已支付"):
            committed += amount
        if state == "已支付":
            paid += amount
        if state == "待询价":
            issue("needs_review", "estimated_quote", key, "Estimated unit price needs a real quotation.")
    currency = text(data.get("currency"), "currency")
    if currencies and currencies != {currency}:
        issue("failed", "mixed_currency", "budget", "Normalize currencies using confirmed rates before summing.")
    rate = number(data.get("reserve_rate"), "reserve_rate")
    if rate >= 1:
        raise ValueError("reserve_rate must be less than 1")
    basis = data.get("reserve_basis")
    if basis not in ("base", "total"):
        raise ValueError("reserve_basis must be base or total")
    reserve = (base * rate if basis == "base" else base / (1 - rate) - base).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if len(currencies) <= 1 and (not currencies or currency in currencies):
        total = base + reserve
        ceiling = data.get("ceiling")
        if missing(ceiling):
            issue("needs_review", "missing_ceiling", "budget", "Budget ceiling is not confirmed.")
        elif total > number(ceiling, "ceiling"):
            issue("failed", "over_budget", "budget", "Planned cost including reserve exceeds the ceiling.")
        computed.update({"known_base": str(base), "reserve": str(reserve), "known_total": str(total),
                         "committed": str(committed), "paid": str(paid), "currency": currency})
        # Unknown quotes make the known total a lower bound, not a full forecast.
        computed["amounts_complete"] = all(not missing(row.get("unit_price")) for row in lines) and bool(lines)
    indexed = {}
    for row in tasks:
        key = text(row.get("id"), "tasks.id")
        if key in indexed:
            raise ValueError("duplicate task ID: " + key)
        indexed[key] = row
        for role in ("R", "A"):
            people = row.get(role)
            if not isinstance(people, list) or any(not isinstance(p, str) or missing(p) for p in people):
                raise ValueError(key + ": roles must be arrays of confirmed person IDs")
            if not people:
                issue("needs_review", "missing_role", key + "." + role, "Task responsibility is not assigned.")
            elif role == "A" and len(people) != 1:
                issue("failed", "multiple_accountable", key, "Each task must have exactly one accountable person.")
        start, end = day(row.get("start")), day(row.get("end"))
        if end < start:
            issue("failed", "task_dates", key, "Task ends before it starts.")
        deps = row.get("depends_on", [])
        if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps):
            raise ValueError(key + ": depends_on must be an array of task IDs")
    indegree = {key: 0 for key in indexed}
    children = {key: [] for key in indexed}
    for key, row in indexed.items():
        for dep in set(row.get("depends_on", [])):
            if dep not in indexed:
                issue("failed", "unknown_dependency", key, "Unknown predecessor: " + dep)
                continue
            indegree[key] += 1
            children[dep].append(key)
            if day(row["start"]) < day(indexed[dep]["end"]):
                issue("failed", "dependency_dates", key, "Task starts before its predecessor finishes.")
    queue = [key for key, count in indegree.items() if count == 0]
    visited = 0
    while queue:
        key = queue.pop()
        visited += 1
        for child in children[key]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(indexed):
        issue("failed", "dependency_cycle", "tasks", "Dependencies contain a cycle.")


if __name__ == "__main__":
    sys.exit(main())
