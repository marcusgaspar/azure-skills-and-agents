"""Synthetic tests for Azure Pricing Calculator plan reconciliation."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from prepare_estimate import prepare, unique_keys


def plan_fixture():
    return {
        "schema_version": "1.0",
        "estimate_name": "Synthetic Azure estimate",
        "currency": "USD",
        "price_reference_date": "2026-01-31",
        "purchase_scenario": "PAYG",
        "tolerance_usd": "0.01",
        "declared_expected_total": "120.00",
        "components": [
            {
                "id": "C001",
                "source_reference": "synthetic!A1",
                "source_service": "Synthetic compute",
                "azure_product": "Virtual Machines",
                "display_name": "Synthetic application VM",
                "region": "Brazil South",
                "quantity": "744",
                "unit": "hour",
                "expected_monthly_cost": "100.00",
                "status": "PREMISSA",
                "representability": "DIRECT",
                "notes": "Synthetic fixture; not an Azure price.",
            },
            {
                "id": "C002",
                "source_reference": "synthetic!A2",
                "source_service": "Synthetic external model",
                "azure_product": "Third-party model",
                "display_name": "Synthetic excluded model usage",
                "region": "Global",
                "quantity": "1",
                "unit": "month",
                "expected_monthly_cost": "20.00",
                "status": "CONFIRMADO",
                "representability": "NOT_REPRESENTABLE",
                "notes": "Synthetic fixture intentionally absent from the calculator.",
            },
        ],
        "calculator_modules": [
            {
                "id": "M001",
                "component_ids": ["C001"],
                "calculator_product": "Virtual Machines",
                "display_name": "Synthetic application VM",
                "region": "Brazil South",
                "configuration": {
                    "operatingSystem": "linux",
                    "size": "f4sv2",
                    "count": "1",
                    "hours": "744",
                    "computeBillingOption": "pay-as-you-go",
                },
                "derivation": "Direct synthetic mapping from component C001.",
            }
        ],
    }


def portal_fixture():
    return {
        "estimate_name": "Synthetic Azure estimate",
        "currency": "USD",
        "query_date": "2026-02-01",
        "total_portal": "105.00",
        "modules": [
            {
                "id": "M001",
                "actual_monthly_cost": "105.00",
                "evidence": "Synthetic rendered subtotal.",
            }
        ],
        "adjustments": [
            {
                "id": "A001",
                "category": "CURRENT_PRICE",
                "amount": "5.00",
                "component_ids": ["C001"],
                "evidence": "Synthetic price-date difference.",
            }
        ],
        "share_url": "https://azure.com/e/synthetic",
        "link_validation": {
            "observed_estimate_name": "Synthetic Azure estimate",
            "observed_currency": "USD",
            "observed_total": "105.00",
            "evidence": "Synthetic new-session validation.",
        },
    }


class PrepareEstimateTests(unittest.TestCase):
    def test_plan_totals(self):
        result = prepare(plan_fixture())
        self.assertEqual(result["status"], "PREPARED")
        self.assertEqual(result["plan_summary"]["expected_total"], "120")
        self.assertEqual(result["plan_summary"]["represented_expected"], "100")
        self.assertEqual(result["plan_summary"]["unrepresented_expected"], "20")
        self.assertEqual(
            result["plan_summary"]["not_representable_component_ids"], ["C002"]
        )

    def test_full_reconciliation(self):
        result = prepare(plan_fixture(), portal_fixture())
        self.assertEqual(result["status"], "RECONCILED_AND_VALIDATED")
        self.assertEqual(result["portal_summary"]["pricing_rule_delta"], "5")
        self.assertEqual(result["portal_summary"]["net_delta"], "-15")
        self.assertEqual(result["portal_summary"]["unexplained_delta"], "0")
        self.assertEqual(result["portal_summary"]["identity_delta"], "0")

    def test_reconciled_without_share(self):
        portal = portal_fixture()
        portal["share_url"] = None
        portal["link_validation"] = None
        result = prepare(plan_fixture(), portal)
        self.assertEqual(result["status"], "RECONCILED_NOT_SHARED")

    def test_missing_cost_is_a_definir(self):
        plan = plan_fixture()
        plan["components"][0]["expected_monthly_cost"] = None
        plan["declared_expected_total"] = None
        result = prepare(plan)
        self.assertEqual(result["status"], "A DEFINIR")
        self.assertEqual(
            result["plan_summary"]["missing_cost_component_ids"], ["C001"]
        )

    def test_a_definir_status_is_unresolved(self):
        plan = plan_fixture()
        plan["components"][1]["status"] = "A DEFINIR"
        result = prepare(plan)
        self.assertEqual(result["status"], "A DEFINIR")
        self.assertEqual(
            result["plan_summary"]["status_a_definir_component_ids"], ["C002"]
        )

    def test_unexplained_adjustment_is_unresolved(self):
        portal = portal_fixture()
        portal["adjustments"][0]["amount"] = "4.00"
        result = prepare(plan_fixture(), portal)
        self.assertEqual(result["status"], "A DEFINIR")
        self.assertEqual(result["portal_summary"]["unexplained_delta"], "1")

    def test_portal_module_total_mismatch_is_unresolved(self):
        portal = portal_fixture()
        portal["total_portal"] = "106.00"
        portal["link_validation"]["observed_total"] = "106.00"
        portal["adjustments"][0]["amount"] = "6.00"
        result = prepare(plan_fixture(), portal)
        self.assertEqual(result["status"], "A DEFINIR")
        self.assertEqual(result["portal_summary"]["portal_module_total_delta"], "-1")

    def test_share_link_content_mismatch_is_unresolved(self):
        portal = portal_fixture()
        portal["link_validation"]["observed_total"] = "104.00"
        result = prepare(plan_fixture(), portal)
        self.assertEqual(result["status"], "A DEFINIR")
        self.assertFalse(result["portal_summary"]["share_link_validated"])

    def test_rejects_float_numbers(self):
        plan = plan_fixture()
        plan["components"][0]["expected_monthly_cost"] = 100.0
        with self.assertRaises(ValueError):
            prepare(plan)
        plan = plan_fixture()
        plan["calculator_modules"][0]["configuration"]["hours"] = 744
        with self.assertRaises(ValueError):
            prepare(plan)

    def test_rejects_duplicate_or_invalid_references(self):
        plan = plan_fixture()
        plan["components"][1]["id"] = "C001"
        with self.assertRaises(ValueError):
            prepare(plan)
        plan = plan_fixture()
        plan["calculator_modules"][0]["component_ids"].append("C002")
        with self.assertRaises(ValueError):
            prepare(plan)

    def test_rejects_unknown_fields_and_duplicate_json_keys(self):
        plan = plan_fixture()
        plan["unexpected"] = True
        with self.assertRaises(ValueError):
            prepare(plan)
        with self.assertRaises(ValueError):
            json.loads('{"currency":"USD","currency":"BRL"}', object_pairs_hook=unique_keys)

    def test_cli_examples_and_no_overwrite(self):
        script = Path(__file__).with_name("prepare_estimate.py")
        root = script.parent.parent
        plan = root / "examples" / "estimate-plan.sample.json"
        portal = root / "examples" / "portal-results.sample.json"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            command = [
                sys.executable,
                str(script),
                str(plan),
                "--portal-results",
                str(portal),
                "--output",
                str(output),
            ]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "RECONCILED_AND_VALIDATED")
            preserved = output.read_bytes()
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(output.read_bytes(), preserved)

    def test_cli_rejects_skill_input_and_output(self):
        script = Path(__file__).with_name("prepare_estimate.py")
        root = script.parent.parent
        run = subprocess.run(
            [sys.executable, str(script), str(root / "SKILL.md")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(run.returncode, 2)
        self.assertIn("skill directory", run.stderr)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "plan.json"
            source.write_text(json.dumps(plan_fixture()), encoding="utf-8")
            run = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(source),
                    "--output",
                    str(root / "forbidden-output.json"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 2)
            self.assertFalse((root / "forbidden-output.json").exists())

    def test_input_objects_are_not_mutated(self):
        plan = plan_fixture()
        portal = portal_fixture()
        original_plan = copy.deepcopy(plan)
        original_portal = copy.deepcopy(portal)
        prepare(plan, portal)
        self.assertEqual(plan, original_plan)
        self.assertEqual(portal, original_portal)


if __name__ == "__main__":
    unittest.main()
