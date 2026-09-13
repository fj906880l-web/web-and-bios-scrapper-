#!/usr/bin/env python3
"""
Unit Tests for BIOS Scanner & Post-Update Drift Remediation Agent
File: tests/test_drift_remediation.py
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Ensure repository root is on sys.path for both package and standalone execution
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from scripts import drift_remediation
from scripts.drift_remediation import SystemDriftAgent


class TestSystemDriftAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SystemDriftAgent()

    def test_capture_firmware_and_os_info_structure(self):
        info = self.agent.capture_firmware_and_os_info()
        self.assertIn("os_type", info)
        self.assertIn("firmware_version", info)
        self.assertIn("architecture", info)
        self.assertIn("captured_at", info)
        self.assertIsInstance(info["firmware_version"], str)
        self.assertTrue(len(info["firmware_version"]) > 0)

    def test_capture_privacy_and_security_states(self):
        states = self.agent.capture_privacy_and_security_states()
        self.assertIsInstance(states, dict)
        self.assertIn("TelemetryServicesDisabled", states)
        self.assertTrue(states["TelemetryServicesDisabled"])
        if self.agent.os_type == "Darwin":
            self.assertIn("SystemIntegrityProtection", states)
            self.assertIn("FileVaultEnabled", states)
            self.assertIn("GatekeeperEnabled", states)
            self.assertIn("ApplicationFirewallEnabled", states)

    def test_baseline_creation_and_hash_integrity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_baseline = drift_remediation.BASELINE_FILE
            test_baseline_file = os.path.join(tmpdir, "test_baseline.json")
            try:
                drift_remediation.BASELINE_FILE = test_baseline_file
                baseline = self.agent.create_baseline()
                self.assertTrue(os.path.exists(test_baseline_file))
                self.assertIn("manifest_hash", baseline)
                self.assertEqual(len(baseline["manifest_hash"]), 64)
                self.assertIn("firmware_baseline", baseline)
                self.assertIn("security_states_baseline", baseline)
            finally:
                drift_remediation.BASELINE_FILE = orig_baseline

    def test_clean_scan_zero_drift(self):
        scan = self.agent.detect_drift()
        self.assertIsInstance(scan, dict)
        self.assertIn("drift_detected", scan)
        self.assertIn("system_health", scan)
        self.assertIn("hardware_security_compliant", scan)

    def test_equipment_update_and_setting_turned_off_darwin(self):
        """Verify that an equipment update with turned-off security controls is caught."""
        baseline_state = {
            "version": "2.0",
            "firmware_baseline": {
                "os_type": "Darwin",
                "firmware_version": "18000.161.10",
                "os_build": "25G83",
                "model_identifier": "Mac14,3"
            },
            "security_states_baseline": {
                "SystemIntegrityProtection": True,
                "FileVaultEnabled": True,
                "ApplicationFirewallEnabled": True,
                "AutoSubmitDiagnostic": False
            }
        }

        simulated_post_update = {
            "firmware_baseline": {
                "os_type": "Darwin",
                "firmware_version": "19000.100.5",  # Updated!
                "os_build": "26A99",               # Updated!
                "model_identifier": "Mac14,3"
            },
            "security_states_baseline": {
                "SystemIntegrityProtection": False,  # Turned OFF!
                "FileVaultEnabled": True,
                "ApplicationFirewallEnabled": False,  # Turned OFF!
                "AutoSubmitDiagnostic": True         # Reset to default ON!
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            orig_baseline = drift_remediation.BASELINE_FILE
            test_baseline_file = os.path.join(tmpdir, "test_baseline.json")
            try:
                drift_remediation.BASELINE_FILE = test_baseline_file
                with open(test_baseline_file, "w") as f:
                    json.dump(baseline_state, f)

                scan = self.agent.detect_drift(simulated_state=simulated_post_update)
                self.assertTrue(scan["equipment_update_detected"])
                self.assertTrue(scan["drift_detected"])
                self.assertEqual(scan["drift_count"], 5)
                self.assertIn("SystemIntegrityProtection", scan["settings_turned_off"])
                self.assertIn("ApplicationFirewallEnabled", scan["settings_turned_off"])
                self.assertIn("AutoSubmitDiagnostic", scan["settings_reset_to_default"])
                self.assertEqual(scan["system_health"], "CRITICAL_DRIFT")
                self.assertFalse(scan["hardware_security_compliant"])
            finally:
                drift_remediation.BASELINE_FILE = orig_baseline

    def test_windows_bios_and_secureboot_turned_off(self):
        """Verify Windows BIOS flash where SecureBoot & VT-x get disabled and telemetry resets."""
        baseline_state = {
            "version": "2.0",
            "firmware_baseline": {
                "os_type": "Windows",
                "firmware_version": "UEFI-v1.8.0",
                "os_build": "22621",
                "model_identifier": "ThinkPad-P1"
            },
            "security_states_baseline": {
                "SecureBootEnabled": True,
                "VirtualizationFirmwareEnabled": True,
                "TPMEnabled": True,
                "AllowTelemetry": False,
                "DisableConsumerFeatures": True
            }
        }

        simulated_windows_drift = {
            "firmware_baseline": {
                "os_type": "Windows",
                "firmware_version": "UEFI-v2.0.1",  # Upgraded BIOS!
                "os_build": "22631",               # Upgraded build!
                "model_identifier": "ThinkPad-P1"
            },
            "security_states_baseline": {
                "SecureBootEnabled": False,          # Turned back OFF by BIOS update!
                "VirtualizationFirmwareEnabled": False,  # Turned OFF!
                "TPMEnabled": True,
                "AllowTelemetry": True,              # Reset to default ON!
                "DisableConsumerFeatures": False     # Reset to default bloat ON!
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            orig_baseline = drift_remediation.BASELINE_FILE
            test_baseline_file = os.path.join(tmpdir, "test_win_baseline.json")
            try:
                drift_remediation.BASELINE_FILE = test_baseline_file
                with open(test_baseline_file, "w") as f:
                    json.dump(baseline_state, f)

                scan = self.agent.detect_drift(simulated_state=simulated_windows_drift)
                self.assertTrue(scan["equipment_update_detected"])
                self.assertIn("SecureBootEnabled", scan["settings_turned_off"])
                self.assertIn("VirtualizationFirmwareEnabled", scan["settings_turned_off"])
                self.assertIn("AllowTelemetry", scan["settings_reset_to_default"])
                self.assertIn("DisableConsumerFeatures", scan["settings_reset_to_default"])
                self.assertEqual(scan["critical_drift_count"], 2)
            finally:
                drift_remediation.BASELINE_FILE = orig_baseline

    def test_remediation_firmware_instructions(self):
        """Verify remediation outputs itemized firmware actions when BIOS settings are OFF."""
        simulated_scan = {
            "scanned_at": "2026-09-13T09:00:00Z",
            "os_type": "Windows",
            "firmware_version": "BIOS-v2.0.1",
            "equipment_update_detected": True,
            "drift_detected": True,
            "drift_count": 2,
            "critical_drift_count": 1,
            "high_drift_count": 1,
            "settings_turned_off": ["SecureBootEnabled"],
            "settings_reset_to_default": ["AllowTelemetry"],
            "drift_events": [
                {
                    "type": "SETTING_TURNED_OFF",
                    "severity": "CRITICAL",
                    "component": "SecureBootEnabled",
                    "is_firmware_setting": True,
                    "remediation_action": "RESTORE_FIRMWARE_SECURITY_SecureBootEnabled"
                },
                {
                    "type": "SETTING_RESET_TO_DEFAULT",
                    "severity": "HIGH",
                    "component": "AllowTelemetry",
                    "is_firmware_setting": False,
                    "remediation_action": "REAPPLY_BASELINE_AllowTelemetry"
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            orig_audit = drift_remediation.AUDIT_LOG_FILE
            test_audit_file = os.path.join(tmpdir, "test_audit.json")
            try:
                drift_remediation.AUDIT_LOG_FILE = test_audit_file
                with patch.object(self.agent, "_run_cmd", return_value=(0, "", "")):
                    result = self.agent.remediate_drift(simulated_scan=simulated_scan)

                self.assertTrue(os.path.exists(test_audit_file))
                self.assertEqual(result["status"], "REMEDIATED")
                self.assertTrue(any("BIOS ACTION REQUIRED" in item for item in result["firmware_instructions"]))
                self.assertIn("SecureBootEnabled", result["settings_turned_off"])
            finally:
                drift_remediation.AUDIT_LOG_FILE = orig_audit


if __name__ == "__main__":
    unittest.main()
