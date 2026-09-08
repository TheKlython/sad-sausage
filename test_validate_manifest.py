"""
test_validate_manifest.py
=========================
Automated unit tests for `validate_manifest.py`.

GUIDANCE FOR AI AGENTS:
-----------------------
- This test suite ensures schema validity and Security-by-Design
  validation rules for 'agent_manifest.json'.
- Covers both positive tests (valid manifests) and negative tests
  (security violations, tamper attempts, malformed JSON).
- Execution: `python -m unittest test_validate_manifest.py`
"""

import json
import os
import tempfile
import unittest

from validate_manifest import validate_agent_manifest, EXPECTED_BTC_ADDRESS


class TestAgentManifestValidator(unittest.TestCase):
    """
    Test suite for agent manifest validation logic.
    """

    def setUp(self):
        """
        Creates a temporary directory for test fixtures.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.valid_data = {
            "project_name": "Sad Sausage Test",
            "agent_id": "test-agent-01",
            "version": "1.0.0",
            "donation": {
                "network": "Bitcoin",
                "symbol": "BTC",
                "address": EXPECTED_BTC_ADDRESS
            },
            "targets": [
                {
                    "name": "GPU Upgrade",
                    "estimated_cost_usd": 1500
                }
            ]
        }

    def tearDown(self):
        """
        Cleans up temporary directory after test execution.
        """
        self.temp_dir.cleanup()

    def _write_manifest(self, filename: str, data_dict: dict) -> str:
        """
        Helper method to write JSON test fixture.
        """
        filepath = os.path.join(self.temp_dir.name, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f)
        return filepath

    def test_valid_manifest(self):
        """
        Tests a properly structured valid manifest.
        """
        filepath = self._write_manifest("valid_manifest.json", self.valid_data)
        is_valid, message = validate_agent_manifest(filepath)
        self.assertTrue(is_valid, f"Should be valid, but failed with: {message}")
        self.assertIn("secure", message.lower())

    def test_official_manifest_file(self):
        """
        Tests the actual 'agent_manifest.json' file located in repository root.
        """
        repo_manifest = os.path.join(os.path.dirname(__file__), "agent_manifest.json")
        is_valid, message = validate_agent_manifest(repo_manifest)
        self.assertTrue(is_valid, f"The main manifest is invalid: {message}")

    def test_missing_file(self):
        """
        Tests reaction to a non-existent file path.
        """
        is_valid, message = validate_agent_manifest("non_existent_file_xyz.json")
        self.assertFalse(is_valid)
        self.assertIn("not found", message.lower())

    def test_invalid_btc_address_format(self):
        """
        Tests security rejection of malformed Bitcoin address formats.
        """
        bad_data = dict(self.valid_data)
        bad_data["donation"] = {
            "network": "Bitcoin",
            "symbol": "BTC",
            "address": "INVALID_BTC_ADDRESS_123"
        }
        filepath = self._write_manifest("bad_btc.json", bad_data)
        is_valid, message = validate_agent_manifest(filepath)
        self.assertFalse(is_valid)
        self.assertIn("invalid bitcoin", message.lower())

    def test_tampered_btc_address(self):
        """
        Tests Security-by-Design defense against address substitution attacks.
        """
        tampered_data = dict(self.valid_data)
        # Valid Bech32 format, but NOT the expected official Sad Sausage address
        tampered_data["donation"] = {
            "network": "Bitcoin",
            "symbol": "BTC",
            "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
        }
        filepath = self._write_manifest("tampered_btc.json", tampered_data)
        is_valid, message = validate_agent_manifest(filepath)
        self.assertFalse(is_valid)
        self.assertIn("security warning", message.lower())

    def test_missing_required_field(self):
        """
        Tests rejection of manifests missing mandatory fields.
        """
        incomplete_data = dict(self.valid_data)
        del incomplete_data["targets"]
        filepath = self._write_manifest("incomplete.json", incomplete_data)
        is_valid, message = validate_agent_manifest(filepath)
        self.assertFalse(is_valid)
        self.assertIn("missing required field", message.lower())


if __name__ == "__main__":
    unittest.main()
