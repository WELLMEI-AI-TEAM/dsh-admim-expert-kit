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
    as_of = day(data.get("as_of"))
    actions = rows(data, "actions")
    if not actions:
        issue("needs_review", "empty_actions", "actions", "No actions to validate; this is not a verified zero-action meeting.")
    seen, overdue = set(), []
    active, complete = 0, 0
    for row in actions:
        key = text(row.get("id"), "actions.id")
        if key in seen:
            issue("failed", "duplicate_id", key, "Action IDs must be unique.")
        seen.add(key)
        for field in ("task", "owner", "acceptance", "source"):
            if missing(row.get(field)):
                issue("needs_review", "missing_field", key + "." + field, "Confirm from the original meeting material.")
            else:
                text(row[field], field)
        state = row.get("status")
        if state not in ("未开始", "进行中", "已完成", "延期", "已取消"):
            issue("failed", "invalid_status", key, "Unknown action status.")
        if state != "已取消":
            active += 1
        if state == "已完成":
            complete += 1
            if missing(row.get("completed_at")) or missing(row.get("evidence")):
                issue("needs_review", "completion_evidence", key, "Completed actions need a completion date and evidence.")
            elif day(row["completed_at"]) > as_of:
                issue("failed", "future_completion", key, "Completion date is after the report date.")
        due = row.get("due")
        if missing(due):
            if state not in ("已完成", "已取消"):
                issue("needs_review", "missing_due", key, "No confirmed due date; do not count as overdue.")
        elif day(due) < as_of and state not in ("已完成", "已取消"):
            overdue.append(key)
            issue("needs_review", "overdue", key, "Past due and still open.")
    computed.update({"active_count": active, "completed_count": complete, "overdue_ids": overdue,
                     "completion_rate": str(Decimal(complete) / active) if active else None})


if __name__ == "__main__":
    sys.exit(main())
