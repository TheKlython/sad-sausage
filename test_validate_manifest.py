"""
test_validate_manifest.py
=========================
Automated unit tests for `validate_manifest.py`.

GUIDANCE FOR AI AGENTS & DEVELOPERS:
-------------------------------------
- This test suite ensures schema validity and anti-phishing
  validation rules for 'agent_manifest.json'.
- Covers positive tests (valid manifests) and negative tests
  (security violations, URL tampering, malformed JSON).
- Execution: `python -m unittest test_validate_manifest.py`
"""

import json
import os
import tempfile
import unittest

from validate_manifest import validate_agent_manifest, EXPECTED_SUPPORT_URL


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
            "version": "2.0.0",
            "support": {
                "platform": "Buy Me a Coffee",
                "url": EXPECTED_SUPPORT_URL
            },
            "targets": [
                {
                    "name": "Host Upgrade",
                    "estimated_cost_eur": 1400,
                    "maintainer_co_investment_eur": 420,
                    "community_target_eur": 980
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

    def test_invalid_support_url_format(self):
        """
        Tests security rejection of malformed support URLs.
        """
        bad_data = dict(self.valid_data)
        bad_data["support"] = {
            "platform": "Buy Me a Coffee",
            "url": "http://insecure-phishing-site.com/fake"
        }
        filepath = self._write_manifest("bad_url.json", bad_data)
        is_valid, message = validate_agent_manifest(filepath)
        self.assertFalse(is_valid)
        self.assertIn("invalid buy me a coffee url", message.lower())

    def test_tampered_support_url(self):
        """
        Tests Security-by-Design defense against URL substitution / phishing attacks.
        """
        tampered_data = dict(self.valid_data)
        tampered_data["support"] = {
            "platform": "Buy Me a Coffee",
            "url": "https://buymeacoffee.com/malicious_attacker"
        }
        filepath = self._write_manifest("tampered_url.json", tampered_data)
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

    def test_co_investment_arithmetic_mismatch(self):
        """
        Tests rejection of manifests where maintainer share + community share != total cost.
        """
        mismatched_data = dict(self.valid_data)
        mismatched_data["targets"] = [
            {
                "name": "Mismatched Target",
                "estimated_cost_eur": 1400,
                "maintainer_co_investment_eur": 420,
                "community_target_eur": 800  # Sum is 1220, but total is 1400!
            }
        ]
        filepath = self._write_manifest("mismatch.json", mismatched_data)
        is_valid, message = validate_agent_manifest(filepath)
        self.assertFalse(is_valid)
        self.assertIn("arithmetic mismatch", message.lower())

    def test_legacy_usd_target_compatibility(self):
        """
        Tests backward compatibility with legacy manifests specifying estimated_cost_usd.
        """
        legacy_data = dict(self.valid_data)
        legacy_data["targets"] = [
            {
                "name": "Legacy USD Target",
                "estimated_cost_usd": 650
            }
        ]
        filepath = self._write_manifest("legacy_usd.json", legacy_data)
        is_valid, message = validate_agent_manifest(filepath)
        self.assertTrue(is_valid, f"Legacy manifest should be valid, but got: {message}")


if __name__ == "__main__":
    unittest.main()
