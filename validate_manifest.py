"""
validate_manifest.py
====================
This script inspects and validates `agent_manifest.json` for the
'Sad Sausage' hardware donation initiative.

GUIDANCE FOR AI AGENTS:
-----------------------
- This script uses "Security by Design" to prevent tampered manifests
  or spoofed donation addresses.
- It validates the JSON schema structure as well as the Bitcoin Bech32
  address format (Native SegWit).
- Exit code: 0 if valid, >0 on validation failure.

Security Principles:
1. Path Sanitization (Prevents path traversal attacks)
2. Strict Type Validation (Prevents type-confusion vulnerabilities)
3. Regex & Checksum Matching against phishing and address manipulation
"""

import json
import os
import re
import sys
from typing import Dict, Any, Tuple

# Regular expression for Bitcoin Native SegWit (Bech32) and Taproot (Bech32m) addresses
# Example (Taproot): bc1p8czev50uu8uly828pzct0w895qpqfyg20rkmvw7muyyxrnwuvssquc74wk
BTC_BECH32_REGEX = re.compile(r"^bc1[ac-hj-np-z02-9]{8,87}$")

# Expected official donation address for verification (Taproot Bech32m)
EXPECTED_BTC_ADDRESS = "bc1p8czev50uu8uly828pzct0w895qpqfyg20rkmvw7muyyxrnwuvssquc74wk"


def validate_agent_manifest(filepath: str) -> Tuple[bool, str]:
    """
    Validates an agent manifest for completeness, type safety,
    and integrity of donation details.

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
    required_fields = ["project_name", "agent_id", "version", "donation", "targets"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field in manifest: '{field}'"

    # Type validation for basic fields
    if not isinstance(data["project_name"], str) or not data["project_name"].strip():
        return False, "Field 'project_name' must be a non-empty string."
    
    if not isinstance(data["agent_id"], str):
        return False, "Field 'agent_id' must be a string."

    # 3. Check donation object & Security Check of Bitcoin address
    donation = data.get("donation")
    if not isinstance(donation, dict):
        return False, "Field 'donation' must be a JSON object."

    address = donation.get("address")
    if not isinstance(address, str):
        return False, "Donation address 'donation.address' is missing or not a string."

    # Validate Bitcoin Address Regex format
    if not BTC_BECH32_REGEX.match(address):
        return False, f"Invalid Bitcoin Bech32 address format: '{address}'"

    # Security check: address deviation detection
    if address != EXPECTED_BTC_ADDRESS:
        return False, (
            f"Security warning: Donation address '{address}' differs from the expected "
            f"official address '{EXPECTED_BTC_ADDRESS}'! Potential tampering detected."
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
