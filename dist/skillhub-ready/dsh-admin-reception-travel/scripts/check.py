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
    segments = rows(data, "segments")
    if not segments:
        issue("needs_review", "empty_segments", "segments", "No itinerary to check.")
    parsed, seen = [], set()
    for row in segments:
        key = text(row.get("id"), "segments.id")
        if key in seen:
            raise ValueError("duplicate segment ID: " + key)
        seen.add(key)
        start, end = stamp(row.get("start")), stamp(row.get("end"))
        if end <= start:
            issue("failed", "nonpositive_duration", key, "End must be after start, including the next date for overnight segments.")
        group, location = text(row.get("group"), "group"), text(row.get("location"), "location")
        resources = row.get("resources", [])
        if not isinstance(resources, list) or any(not isinstance(x, str) or not x.strip() for x in resources):
            raise ValueError(key + ": resources must be nonempty string IDs")
        if row.get("kind") == "meal" and row.get("diet_confirmed") is not True:
            issue("needs_review", "diet_unconfirmed", key, "Confirm dietary restrictions.")
        if row.get("kind") == "visit" and (missing(row.get("guide")) or row.get("permission_confirmed") is not True):
            issue("needs_review", "visit_unconfirmed", key, "Confirm guide and visitor permission.")
        parsed.append((start, end, key, group, location, set(resources), row))
    parsed.sort(key=lambda x: (x[0], x[1], x[2]))
    for i, first in enumerate(parsed):
        for second in parsed[i + 1:]:
            if second[0] >= first[1]:
                break
            if first[3] == second[3] or first[5] & second[5]:
                issue("failed", "resource_overlap", first[2] + "/" + second[2], "Overlapping group or shared resource.")
    groups = {}
    for row in parsed:
        groups.setdefault(row[3], []).append(row)
    for group, sequence in groups.items():
        for first, second in zip(sequence, sequence[1:]):
            if first[4] == second[4] or second[0] < first[1]:
                continue
            required = second[6].get("transfer_minutes")
            if required is None:
                issue("needs_review", "missing_transfer", second[2], "Confirm travel and buffer minutes between different locations.")
            elif Decimal(str((second[0] - first[1]).total_seconds())) < number(required, "transfer_minutes") * 60:
                issue("failed", "transfer_shortfall", first[2] + "/" + second[2], "Insufficient transfer and buffer time.")
    departure = data.get("departure")
    if departure is not None:
        if not isinstance(departure, dict):
            raise ValueError("departure: expected an object")
        at = stamp(departure.get("at"))
        minutes = sum((number(departure.get(k), k) for k in ("travel_minutes", "security_minutes", "buffer_minutes")), Decimal(0))
        from datetime import timedelta
        latest = at - timedelta(seconds=float(minutes * 60))
        group = text(departure.get("group"), "departure.group")
        business = [x for x in groups.get(group, []) if x[6].get("kind") != "transfer"]
        if not business:
            issue("needs_review", "no_departure_group", group, "No business segments found for the departure group.")
        elif max(x[1] for x in business) > latest:
            issue("failed", "departure_missed", group, "Business activities end after the latest station/airport departure.")
        if departure.get("confirmed") is not True:
            issue("needs_review", "departure_unconfirmed", group, "Departure and advance-time parameters are estimates.")
        computed["latest_departure_utc"] = latest.isoformat()
    computed["segments_checked"] = len(parsed)


if __name__ == "__main__":
    sys.exit(main())
