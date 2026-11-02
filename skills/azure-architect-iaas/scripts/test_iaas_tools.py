"""Synthetic tests for IaaS skill helpers; no customer data or Azure prices."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from derive_iaas_requirements import derive, unique_keys
from next_output_version import COST_PREFIX, INVENTORY_PREFIX, next_output_version


def fixture() -> dict:
    return {
        "target_region": None,
        "vms": [
            {
                "id": "vm-1",
                "name": "app-01",
                "source_refs": ["synthetic-rvtools.xlsx!vInfo row 2", "synthetic-cmdb.xlsx!CMDB row 2"],
                "migration_destination": "azure-iaas",
                "exclude_reason": None,
                "cmdb": {
                    "application": "billing",
                    "service": None,
                    "environment": "prod",
                    "dependencies": ["database"],
                },
                "inventory": {"vcpu": "4", "memory_gib": "16", "os": "Windows Server"},
                "metrics": {
                    "observation_days": "30",
                    "peak_covered": True,
                    "cpu_p95_pct": "50",
                    "memory_p95_gib": "10",
                },
                "disks": [
                    {
                        "id": "data",
                        "role": "data",
                        "capacity_gib": "512",
                        "iops_p95": "1200",
                        "throughput_mbps_p95": "80",
                        "shared_requirement": False,
                        "protocol": None,
                    }
                ],
                "rto_minutes": "60",
                "rpo_minutes": "15",
            }
        ],
    }


class DeriveRequirementsTests(unittest.TestCase):
    def test_p95_margin_and_cmdb_group(self):
        result = derive(fixture())
        vm = result["vms"][0]
        self.assertEqual(result["settings"]["target_region"], "Brazil South")
        self.assertEqual(result["settings"]["target_region_status"], "A DEFINIR")
        self.assertEqual(vm["required_vcpu"], "3")
        self.assertEqual(vm["required_memory_gib"], "12.00")
        self.assertEqual(vm["disks"][0]["required_iops"], "1440.00")
        self.assertEqual(vm["execution_group"]["confidence_pct"], "100.00")
        self.assertIn("[SUGESTÃO] Validar elegibilidade de Azure Hybrid Benefit; baseline permanece PAYG.", vm["suggestions"])

    def test_insufficient_metrics_stay_undefined(self):
        data = fixture()
        data["vms"][0]["metrics"]["observation_days"] = "29"
        result = derive(data)
        vm = result["vms"][0]
        self.assertEqual(vm["sizing_status"], "A DEFINIR")
        self.assertIsNone(vm["required_vcpu"])
        self.assertIsNone(vm["disks"][0]["required_iops"])
        self.assertTrue(any(item["id"] == "vm-telemetry" for item in result["questionnaire"]))

    def test_environment_dependency_group_is_exactly_fifty(self):
        data = fixture()
        data["vms"][0]["cmdb"]["application"] = None
        result = derive(data)
        group = result["vms"][0]["execution_group"]
        self.assertEqual(group["confidence_pct"], "50.00")
        self.assertEqual(result["execution_groups"][0]["status"], "ready")

    def test_environment_only_group_is_undefined(self):
        data = fixture()
        data["vms"][0]["cmdb"]["application"] = None
        data["vms"][0]["cmdb"]["dependencies"] = []
        result = derive(data)
        self.assertEqual(result["vms"][0]["execution_group"]["confidence_pct"], "40.00")
        self.assertTrue(any(item["id"] == "execution-group" for item in result["questionnaire"]))

    def test_missing_migration_destination_excludes_vm(self):
        data = fixture()
        data["vms"][0]["migration_destination"] = None
        result = derive(data)
        self.assertEqual(result["summary"]["excluded_vm_count"], 1)
        self.assertEqual(result["vms"][0]["scope"], "excluded")
        self.assertTrue(any(item["id"] == "migration-destination" for item in result["questionnaire"]))

    def test_shared_storage_creates_storage_question(self):
        data = fixture()
        data["vms"][0]["disks"][0]["shared_requirement"] = None
        result = derive(data)
        self.assertTrue(any(item["id"] == "storage-protocol-data" for item in result["questionnaire"]))

    def test_invalid_metrics_are_rejected(self):
        for invalid in ["101", "-1", 50]:
            data = fixture()
            data["vms"][0]["metrics"]["cpu_p95_pct"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                derive(data)

    def test_duplicate_vm_and_disk_ids_are_rejected(self):
        data = fixture()
        data["vms"].append(data["vms"][0].copy())
        with self.assertRaises(ValueError):
            derive(data)
        data = fixture()
        data["vms"][0]["disks"].append(data["vms"][0]["disks"][0].copy())
        with self.assertRaises(ValueError):
            derive(data)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"vms":[],"vms":[]}', object_pairs_hook=unique_keys)


class VersioningTests(unittest.TestCase):
    def test_uses_highest_pair_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / f"{INVENTORY_PREFIX}-v1.xlsx").touch()
            (root / f"{COST_PREFIX}-v3.xlsx").touch()
            version = next_output_version(root)
            self.assertEqual(version["version"], 4)
            self.assertTrue(version["inventory_file"].endswith("-v4.xlsx"))

    def test_cli_writes_once_and_protects_input(self):
        script = Path(__file__).with_name("derive_iaas_requirements.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            output = root / "output.json"
            source.write_text(json.dumps(fixture()), encoding="utf-8")
            command = [sys.executable, str(script), str(source), "--output", str(output)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["summary"]["in_scope_vm_count"], 1)
            before = output.read_bytes()
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(output.read_bytes(), before)
            run = subprocess.run(command[:3] + ["--output", str(source)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)


if __name__ == "__main__":
    unittest.main()
