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
    fields = data.get("fields", {})
    if not isinstance(fields, dict):
        raise ValueError("fields: expected an object")
    for field in ("sender", "recipients", "subject"):
        if missing(fields.get(field)):
            issue("needs_review", "missing_field", field, "Provide or confirm this document fact.")
        else:
            text(fields[field], field)
    dates = rows(data, "dates")
    if not dates:
        issue("needs_review", "no_dates", "dates", "No dates supplied; no date check was performed.")
    indexed = {}
    for row in dates:
        key = text(row.get("id"), "dates.id")
        if key in indexed:
            issue("failed", "duplicate_id", key, "Duplicate date ID.")
        if missing(row.get("date")):
            issue("needs_review", "missing_date", key, "Absolute date is not confirmed.")
            indexed[key] = None
            continue
        value = day(row["date"])
        indexed[key] = value
        weekday = row.get("weekday")
        if weekday is not None:
            if isinstance(weekday, bool) or not isinstance(weekday, int) or not 0 <= weekday <= 6:
                raise ValueError(key + ": weekday must be integer 0 (Monday) to 6 (Sunday)")
            if weekday != value.weekday():
                issue("failed", "weekday_mismatch", key, "Weekday conflicts with the supplied calendar date.")
    for pair in rows(data, "before"):
        a, b = pair.get("earlier"), pair.get("later")
        if a not in indexed or b not in indexed:
            issue("failed", "unknown_date", str(a) + "/" + str(b), "Ordering references an unknown date ID.")
        elif indexed[a] is not None and indexed[b] is not None and indexed[a] > indexed[b]:
            issue("failed", "date_order", a, "This date must not be later than " + b)
    computed["weekdays"] = {key: value.weekday() for key, value in indexed.items() if value is not None}


if __name__ == "__main__":
    sys.exit(main())
