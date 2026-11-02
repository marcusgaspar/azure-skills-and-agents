"""Synthetic arithmetic tests; no Azure prices or customer data."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from recalculate import review, unique_keys


def fixture():
    return {
        "rounding": "total",
        "lines": [
            {"id": "a", "evidence": "synthetic!A1", "factors": ["2", "730", "0.20"]},
            {"id": "b", "evidence": "synthetic!A2", "factors": ["10"]},
            {"id": "c", "evidence": "synthetic!A3", "factors": ["438"]},
        ],
        "portfolios": [
            {"id": "base", "evidence": "synthetic!A4", "line_ids": ["a", "b"], "declared_total": "302"},
            {"id": "fixed", "evidence": "synthetic scenario", "line_ids": ["c", "b"], "declared_total": None},
        ],
        "comparisons": [],
        "impacts": [
            {"id": "change", "evidence": "synthetic calculation", "original": "base",
             "revised": "fixed", "kind": "correction"},
        ],
    }


class ReviewTests(unittest.TestCase):
    def test_reconciliation_and_signed_impact(self):
        result = review(fixture())
        self.assertEqual(result["portfolios"][0]["monthly_usd"], "302.00")
        self.assertEqual(result["portfolios"][0]["reconciliation_status"], "OK")
        self.assertEqual(result["impacts"][0]["monthly_delta_usd"], "146.00")
        self.assertFalse(result["has_missing_values"])

    def test_missing_propagates_and_subtotal_is_labelled(self):
        data = fixture()
        data["lines"][0]["factors"] = ["0", None]
        result = review(data)
        self.assertIsNone(result["portfolios"][0]["monthly_usd"])
        self.assertEqual(result["portfolios"][0]["known_subtotal_usd"], "10.00")
        self.assertIsNone(result["impacts"][0]["monthly_delta_usd"])
        self.assertTrue(result["has_missing_values"])

    def test_divergence(self):
        data = fixture()
        data["portfolios"][0]["declared_total"] = "303"
        result = review(data)
        self.assertEqual(result["portfolios"][0]["delta_usd"], "-1.00")
        self.assertTrue(result["has_divergences"])

    def test_breakdown_omission(self):
        data = fixture()
        data["portfolios"].append({
            "id": "breakdown", "evidence": "synthetic slide", "line_ids": ["a"],
            "declared_total": "292",
        })
        data["comparisons"].append({
            "id": "cross-file", "evidence": "synthetic slide vs sheet",
            "left": "breakdown", "right": "base",
        })
        self.assertEqual(review(data)["comparisons"][0]["delta_usd"], "-10.00")

    def test_duplicate_references_rejected(self):
        data = fixture()
        data["portfolios"][0]["line_ids"] = ["a", "a"]
        with self.assertRaises(ValueError):
            review(data)

    def test_unknown_reference_rejected(self):
        data = fixture()
        data["portfolios"][0]["line_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            review(data)

    def test_numeric_float_and_nonfinite_rejected(self):
        for invalid in [0.20, "NaN", "Infinity", "", "1,200", "1e1000"]:
            data = fixture()
            data["lines"][0]["factors"] = [invalid]
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                review(data)

    def test_evidence_required(self):
        data = fixture()
        data["lines"][0]["evidence"] = ""
        with self.assertRaises(ValueError):
            review(data)

    def test_rounding_explicit(self):
        data = fixture()
        del data["rounding"]
        with self.assertRaises(ValueError):
            review(data)

    def test_line_vs_total_rounding(self):
        data = fixture()
        data["lines"][0]["factors"] = ["0.005"]
        data["lines"][1]["factors"] = ["0.005"]
        self.assertEqual(review(data)["portfolios"][0]["monthly_usd"], "0.01")
        data["rounding"] = "line"
        self.assertEqual(review(data)["portfolios"][0]["monthly_usd"], "0.02")

    def test_alternatives_not_aggregated(self):
        data = fixture()
        data["impacts"][0]["kind"] = "alternative"
        data["impacts"].append({
            **data["impacts"][0], "id": "second-option",
            "original": "fixed", "revised": "base",
        })
        result = review(data)
        self.assertEqual(result["impacts"][1]["monthly_delta_usd"], "-146.00")
        self.assertNotIn("total_savings", result)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"rounding":"total","rounding":"line"}', object_pairs_hook=unique_keys)

    def test_empty_estimate_rejected(self):
        for field in ["lines", "portfolios"]:
            data = fixture()
            data[field] = []
            with self.subTest(field=field), self.assertRaises(ValueError):
                review(data)

    def test_missing_declared_total_is_not_reconciled(self):
        result = review(fixture())
        self.assertEqual(result["portfolios"][1]["reconciliation_status"], "Nao verificado")

    def test_invalid_decimal_syntax_rejected(self):
        for invalid in ["1_000", " 10 ", "+10"]:
            data = fixture()
            data["lines"][0]["factors"] = [invalid]
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                review(data)

    def test_cli_exit_codes_and_no_overwrite(self):
        script = Path(__file__).with_name("recalculate.py")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            output = Path(directory) / "output.json"
            source.write_text(json.dumps(fixture()), encoding="utf-8")
            command = [sys.executable, str(script), str(source), "--output", str(output)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["impacts"][0]["monthly_delta_usd"], "146.00")
            preserved = output.read_bytes()
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(output.read_bytes(), preserved)
            data = fixture()
            data["portfolios"][0]["declared_total"] = "303"
            source.write_text(json.dumps(data), encoding="utf-8")
            run = subprocess.run(command[:3], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            data["lines"][0]["factors"] = [None]
            source.write_text(json.dumps(data), encoding="utf-8")
            run = subprocess.run(command[:3], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            before = source.read_bytes()
            run = subprocess.run(command[:3] + ["--output", str(source)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(source.read_bytes(), before)

    def test_cli_protects_skill_directory(self):
        script = Path(__file__).with_name("recalculate.py")
        run = subprocess.run(
            [sys.executable, str(script), str(script)], capture_output=True, text=True,
        )
        self.assertEqual(run.returncode, 2)
        self.assertIn("skill directory", run.stderr)


if __name__ == "__main__":
    unittest.main()
