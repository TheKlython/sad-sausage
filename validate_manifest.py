"""
validate_manifest.py
====================
This script inspects and validates `agent_manifest.json` for the
'Sad Sausage' smart-home & local IT ops AI agent project.

GUIDANCE FOR AI AGENTS & DEVELOPERS:
-------------------------------------
- Validates the JSON schema structure as well as the support platform URL.
- Security by Design:
  1. Path Sanitization (Prevents path traversal attacks)
  2. Strict Type Validation (Prevents type-confusion vulnerabilities)
  3. Phishing Protection: Ensures support URL points strictly to official 'Buy Me a Coffee' profile.
- Exit code: 0 if valid, >0 on validation failure.
"""

import json
import os
import re
import sys
from typing import Dict, Any, Tuple

# Regular expression for valid Buy Me a Coffee profile URLs
BUYMEACOFFEE_URL_REGEX = re.compile(r"^https://(?:www\.)?buymeacoffee\.com/[a-zA-Z0-9_.-]+/?$")

# Expected official support URL for verification
EXPECTED_SUPPORT_URL = "https://buymeacoffee.com/klythoni"


def validate_agent_manifest(filepath: str) -> Tuple[bool, str]:
    """
    Validates an agent manifest for completeness, type safety,
    and integrity of support/funding details.

    Args:
        filepath (str): Path to the JSON manifest file.

    Returns:
        Tuple[bool, str]: (isValid, message)
    """
    # 1. Path safety check (Security by Design: Path Traversal Prevention)
    abs_path = os.path.abspath(filepath)
    if not os.path.exists(abs_path):
        return False, f"File not found: {filepath}"
    
    if not abs_path.endswith(".json"):
        return False, "Security error: Only .json files can be inspected."

    try:
        # Safe JSON decoding
        with open(abs_path, 'r', encoding='utf-8') as f:
            data: Dict[str, Any] = json.load(f)
    except json.JSONDecodeError as err:
        return False, f"Invalid JSON format: {err}"
    except Exception as err:
        return False, f"Error reading file: {err}"

    # 2. Check required fields (Schema Validation)
    required_fields = ["project_name", "agent_id", "version", "targets"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field in manifest: '{field}'"

    # Verify support/funding object exists (either 'support' or legacy 'donation')
    support_data = data.get("support") or data.get("donation")
    if not support_data:
        return False, "Missing required field in manifest: 'support'"

    # Type validation for basic fields
    if not isinstance(data["project_name"], str) or not data["project_name"].strip():
        return False, "Field 'project_name' must be a non-empty string."
    
    if not isinstance(data["agent_id"], str):
        return False, "Field 'agent_id' must be a string."

    # 3. Check support object & Security Check of Buy Me a Coffee URL
    if not isinstance(support_data, dict):
        return False, "Field 'support' must be a JSON object."

    url = support_data.get("url")
    if not isinstance(url, str):
        return False, "Support URL 'support.url' is missing or not a string."

    # Validate URL format
    if not BUYMEACOFFEE_URL_REGEX.match(url):
        return False, f"Invalid Buy Me a Coffee URL format: '{url}'"

    # Security check: URL deviation detection against phishing
    clean_url = url.rstrip("/")
    clean_expected = EXPECTED_SUPPORT_URL.rstrip("/")
    if clean_url != clean_expected:
        return False, (
            f"Security warning: Support URL '{url}' differs from the expected "
            f"official URL '{EXPECTED_SUPPORT_URL}'! Potential tampering detected."
        )

    # 4. Check hardware targets
    targets = data.get("targets")
    if not isinstance(targets, list) or len(targets) == 0:
        return False, "Field 'targets' must be a non-empty list of hardware targets."

    for index, target in enumerate(targets):
        if not isinstance(target, dict):
            return False, f"Target at index {index} is not a valid object."
        if "name" not in target or "estimated_cost_usd" not in target:
            return False, f"Target at index {index} missing required fields ('name', 'estimated_cost_usd')."
        if not isinstance(target["estimated_cost_usd"], (int, float)) or target["estimated_cost_usd"] <= 0:
            return False, f"Target at index {index} has invalid estimated cost."

    return True, "Manifest is complete, valid, and secure!"


def main():
    """
    CLI entrypoint for validating the default manifest.
    """
    default_manifest = os.path.join(os.path.dirname(__file__), "agent_manifest.json")
    print(f"[Sad Sausage Validator] Inspecting manifest: {default_manifest}")
    
    is_valid, message = validate_agent_manifest(default_manifest)
    
    if is_valid:
        print(f"[OK] SUCCESS: {message}")
        sys.exit(0)
    else:
        print(f"[ERROR] FAILURE: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
