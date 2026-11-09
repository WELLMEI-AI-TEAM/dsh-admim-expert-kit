"""Business boundary regressions; no network or Office needed."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ["admin-notice-docs", "admin-meeting-minutes", "admin-reception-travel",
         "admin-asset-ledger", "admin-event-planning"]
MODULES = {}
for name in NAMES:
    spec = importlib.util.spec_from_file_location(name, ROOT / "skills" / name / "scripts/check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    MODULES[name] = module


def sample(name):
    return json.loads((ROOT / "skills" / name / "references/example.json").read_text(encoding="utf-8"))


def check(name, data):
    return MODULES[name].validate(data)


def codes(report):
    return {x["code"] for x in report["issues"]}


class CommonTests(unittest.TestCase):
    def test_examples_pass(self):
        for name in NAMES:
            with self.subTest(name=name):
                self.assertEqual(check(name, sample(name))["status"], "passed")

    def test_missing_input_never_passes(self):
        for name in NAMES:
            with self.subTest(name=name):
                self.assertNotEqual(check(name, {})["status"], "passed")

    def test_wrong_root_type_is_structured_error(self):
        for name in NAMES:
            self.assertEqual(check(name, [1, 2])["status"], "failed")

    def test_no_input_mutation(self):
        for name in NAMES:
            data = sample(name)
            original = copy.deepcopy(data)
            check(name, data)
            self.assertEqual(data, original)

    def test_cli_exit_codes_and_invalid_json(self):
        name = "admin-meeting-minutes"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "input.json"
            for content, status, expected in [(json.dumps(sample(name)), "passed", 0),
                                             ('{"as_of":"2026-11-09","actions":[]}', "needs_review", 2),
                                             ("{", "failed", 1)]:
                path.write_text(content, encoding="utf-8")
                run = subprocess.run([sys.executable, "-B", str(ROOT / "skills" / name / "scripts/check.py"), str(path)], capture_output=True, encoding="utf-8")
                self.assertEqual(run.returncode, expected, run.stderr)
                self.assertEqual(json.loads(run.stdout)["status"], status)


class NoticeTests(unittest.TestCase):
    name = "admin-notice-docs"

    def test_wrong_weekday(self):
        data = sample(self.name)
        data["dates"][0]["weekday"] = 0
        self.assertIn("weekday_mismatch", codes(check(self.name, data)))

    def test_deadline_after_event(self):
        data = sample(self.name)
        data["dates"][0].update(date="2026-11-14", weekday=5)
        self.assertIn("date_order", codes(check(self.name, data)))

    def test_unknown_date_and_missing_fact(self):
        data = sample(self.name)
        data["fields"]["sender"] = "【待确认：发文单位】"
        data["before"][0]["earlier"] = "missing"
        self.assertTrue({"missing_field", "unknown_date"} <= codes(check(self.name, data)))

    def test_invalid_calendar_date(self):
        data = sample(self.name)
        data["dates"][0]["date"] = "2026-02-30"
        self.assertEqual(check(self.name, data)["status"], "failed")


class MeetingTests(unittest.TestCase):
    name = "admin-meeting-minutes"

    def test_blank_due_is_missing_not_overdue(self):
        data = sample(self.name)
        data["actions"][0]["due"] = None
        report = check(self.name, data)
        self.assertIn("missing_due", codes(report))
        self.assertEqual(report["computed"]["overdue_ids"], [])

    def test_past_due_open_action(self):
        data = sample(self.name)
        data["actions"][0]["due"] = "2026-11-08"
        self.assertEqual(check(self.name, data)["computed"]["overdue_ids"], ["A1"])

    def test_cancelled_excluded_from_denominator(self):
        data = sample(self.name)
        data["actions"][0]["status"] = "已取消"
        self.assertIsNone(check(self.name, data)["computed"]["completion_rate"])

    def test_completion_needs_evidence(self):
        data = sample(self.name)
        data["actions"][0]["status"] = "已完成"
        self.assertIn("completion_evidence", codes(check(self.name, data)))

    def test_done_and_cancelled_rate(self):
        data = sample(self.name)
        data["actions"][0].update(status="已完成", completed_at="2026-11-08", evidence="归档文件#1")
        cancelled = copy.deepcopy(data["actions"][0])
        cancelled.update(id="A2", status="已取消")
        data["actions"].append(cancelled)
        report = check(self.name, data)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["computed"]["completion_rate"], "1")

    def test_duplicate_action(self):
        data = sample(self.name)
        data["actions"].append(copy.deepcopy(data["actions"][0]))
        self.assertIn("duplicate_id", codes(check(self.name, data)))


class InventoryTests(unittest.TestCase):
    name = "admin-asset-ledger"

    def test_returns_and_loss(self):
        result = check(self.name, sample(self.name))["computed"]["items"][0]
        self.assertEqual(result["closing"], "9")  # 10+5+1-6-1
        self.assertEqual(result["net_usage"], "5")
        self.assertEqual(result["usage_amount"], "100.00")

    def test_count_sign_and_missing_actual(self):
        data = sample(self.name)
        data["items"][0]["actual"] = "7"
        self.assertEqual(check(self.name, data)["computed"]["items"][0]["stocktake_difference"], "-2")
        data["items"][0]["actual"] = None
        data["stocktake"] = True
        report = check(self.name, data)
        self.assertIn("not_counted", codes(report))
        self.assertIsNone(report["computed"]["items"][0]["stocktake_difference"])

    def test_historical_price_not_current_price(self):
        data = sample(self.name)
        data["items"][0]["current_price"] = "9999"
        self.assertEqual(check(self.name, data)["computed"]["items"][0]["usage_amount"], "100.00")

    def test_missing_price_remains_unknown(self):
        data = sample(self.name)
        data["movements"][1]["unit_price"] = None
        report = check(self.name, data)
        self.assertIn("missing_price", codes(report))
        self.assertIsNone(report["computed"]["items"][0]["usage_amount"])

    def test_duplicate_movement_not_counted_twice(self):
        data = sample(self.name)
        data["movements"].append(copy.deepcopy(data["movements"][1]))
        report = check(self.name, data)
        self.assertIn("duplicate_movement", codes(report))
        self.assertEqual(report["computed"]["items"][0]["closing"], "9")

    def test_negative_stock_and_unknown_item(self):
        data = sample(self.name)
        data["movements"][1]["quantity"] = "60"
        extra = copy.deepcopy(data["movements"][0])
        extra.update(id="unknown", item_id="not-in-master")
        data["movements"].append(extra)
        self.assertTrue({"negative_stock", "unknown_item"} <= codes(check(self.name, data)))

    def test_period_filter_and_units(self):
        data = sample(self.name)
        data["movements"][1]["date"] = "2026-10-31"
        self.assertEqual(check(self.name, data)["computed"]["items"][0]["closing"], "15")
        data["movements"][1].update(date="2026-11-03", unit="盒")
        self.assertIn("unit_mismatch", codes(check(self.name, data)))

    def test_nonfinite_and_negative_quantities(self):
        for value in ("NaN", "Infinity", "-1", True, "0"):
            data = sample(self.name)
            data["movements"][0]["quantity"] = value
            with self.subTest(value=value):
                self.assertEqual(check(self.name, data)["status"], "failed")


class TravelTests(unittest.TestCase):
    name = "admin-reception-travel"

    def test_nested_overlap_not_just_adjacent(self):
        data = sample(self.name)
        first = data["segments"][0]
        first["end"] = "2026-11-10T17:00:00+08:00"
        second = copy.deepcopy(first)
        second.update(id="S2", start="2026-11-10T14:00:00+08:00", end="2026-11-10T14:30:00+08:00", group="other", resources=[])
        third = copy.deepcopy(first)
        third.update(id="S3", start="2026-11-10T15:00:00+08:00", end="2026-11-10T16:00:00+08:00")
        data["segments"] = [first, second, third]
        report = check(self.name, data)
        self.assertTrue(any(x["code"] == "resource_overlap" and x["ref"] == "S1/S3" for x in report["issues"]))

    def test_parallel_groups_allowed_unless_shared_resource(self):
        data = sample(self.name)
        first = data["segments"][0]
        second = copy.deepcopy(first)
        second.update(id="S2", group="other", resources=["other-room"])
        data["segments"] = [first, second]
        self.assertNotIn("resource_overlap", codes(check(self.name, data)))
        second["resources"] = first["resources"]
        self.assertIn("resource_overlap", codes(check(self.name, data)))

    def test_overnight_and_timezone_equivalence(self):
        data = sample(self.name)
        data.pop("departure")
        first = data["segments"][0]
        first.update(start="2026-11-10T23:40:00+08:00", end="2026-11-11T00:20:00+08:00")
        data["segments"] = [first]
        self.assertEqual(check(self.name, data)["status"], "passed")
        second = copy.deepcopy(first)
        second.update(id="S2", start="2026-11-10T15:50:00Z", end="2026-11-10T16:10:00Z")
        data["segments"].append(second)
        self.assertIn("resource_overlap", codes(check(self.name, data)))

    def test_transfer_and_departure_cutoff(self):
        data = sample(self.name)
        data["segments"][1]["transfer_minutes"] = 30
        self.assertIn("transfer_shortfall", codes(check(self.name, data)))
        data["segments"][1]["end"] = "2026-11-10T18:00:00+08:00"
        self.assertIn("departure_missed", codes(check(self.name, data)))

    def test_cutoff_has_independent_expected_value(self):
        # 18:40 - 40 road - 30 station - 15 buffer = 17:15 local = 09:15 UTC.
        self.assertEqual(check(self.name, sample(self.name))["computed"]["latest_departure_utc"], "2026-11-10T09:15:00+00:00")

    def test_no_timezone_rejected(self):
        data = sample(self.name)
        data["segments"][0]["start"] = "2026-11-10T13:00:00"
        self.assertEqual(check(self.name, data)["status"], "failed")


class EventTests(unittest.TestCase):
    name = "admin-event-planning"

    def test_reserve_bases(self):
        data = sample(self.name)
        self.assertEqual(check(self.name, data)["computed"]["known_total"], "1080.00")
        data["reserve_basis"] = "total"
        self.assertEqual(check(self.name, data)["computed"]["reserve"], "86.96")
        self.assertEqual(check(self.name, data)["computed"]["known_total"], "1086.96")

    def test_paid_still_committed(self):
        data = sample(self.name)
        data["budget"][0]["status"] = "已支付"
        result = check(self.name, data)["computed"]
        self.assertEqual(result["paid"], "1000.00")
        self.assertEqual(result["committed"], "1000.00")

    def test_unknown_quote_and_overspend(self):
        data = sample(self.name)
        data["ceiling"] = "500"
        extra = copy.deepcopy(data["budget"][0])
        extra.update(id="B2", unit_price=None)
        data["budget"].append(extra)
        report = check(self.name, data)
        self.assertTrue({"over_budget", "missing_quote"} <= codes(report))
        self.assertFalse(report["computed"]["amounts_complete"])

    def test_mixed_currency_not_summed(self):
        data = sample(self.name)
        extra = copy.deepcopy(data["budget"][0])
        extra.update(id="B2", currency="USD")
        data["budget"].append(extra)
        report = check(self.name, data)
        self.assertIn("mixed_currency", codes(report))
        self.assertNotIn("known_total", report["computed"])

    def test_multiple_A_and_dependency_cycle(self):
        data = sample(self.name)
        data["tasks"][0]["A"] = ["张", "李"]
        data["tasks"][0]["depends_on"] = ["T2"]
        self.assertTrue({"multiple_accountable", "dependency_cycle"} <= codes(check(self.name, data)))

    def test_missing_role_and_unknown_predecessor(self):
        data = sample(self.name)
        data["tasks"][0]["R"] = []
        data["tasks"][0]["depends_on"] = ["not-found"]
        self.assertTrue({"missing_role", "unknown_dependency"} <= codes(check(self.name, data)))

    def test_dependency_date_order(self):
        data = sample(self.name)
        data["tasks"][1]["start"] = "2026-11-09"
        self.assertIn("dependency_dates", codes(check(self.name, data)))

    def test_decimal_rounding_per_line(self):
        data = sample(self.name)
        data["budget"][0].update(unit_price="0.105", quantity="1")
        data["reserve_rate"] = "0"
        self.assertEqual(check(self.name, data)["computed"]["known_total"], "0.11")

    def test_reserve_rate_one_rejected(self):
        data = sample(self.name)
        data["reserve_rate"] = "1"
        self.assertEqual(check(self.name, data)["status"], "failed")


if __name__ == "__main__":
    unittest.main()
