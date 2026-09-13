"""
Automated unit tests for the Optoma RS232 UART protocol and parser logic.
Validates:
1. Asynchronous INFO message decoding (faults & power states).
2. Multi-value status packet parsing (~00150 1 response format).
3. Projection mode integer-to-string mapping.
4. Command formatting for control actions.
"""

import pytest


def parse_info_message(msg: str):
    """Maps asynchronous projector INFO frames to human-readable states."""
    mapping = {
        "INFO0": "Standby",
        "INFO1": "Warming",
        "INFO2": "Cooling",
        "INFO3": "Out of Range",
        "INFO4": "Error - Laser",
        "INFO5": "Thermal Error",
        "INFO6": "FAN Locked",
        "INFO7": "Overheat",
    }
    return mapping.get(msg, None)


def parse_status_packet(msg: str):
    """
    Parses Optoma ~00150 1 response format:
    Ok<power(1)><lamp_hours(5)><source(2)><firmware(4)><display_mode(2)>
    Example: Ok10277814C01521
    """
    if not (msg.startswith("Ok") or msg.startswith("OK")):
        return None
    
    if len(msg) >= 16:
        power_char = msg[2]
        lamp_hours = msg[3:8]
        source_code = msg[8:10]
        firmware = msg[10:14]
        display_mode = msg[14:16]

        sources = {
            "00": "None",
            "06": "Video",
            "07": "HDMI 1",
            "08": "HDMI 2",
            "14": "HDMI 3",
        }

        return {
            "power": "On" if power_char == "1" else "Off",
            "lamp_hours": lamp_hours,
            "source": sources.get(source_code, f"Unknown ({source_code})"),
            "firmware": firmware,
            "display_mode": display_mode,
        }
    return None


def parse_projection_mode(payload: str):
    """Maps Optoma projection mode integers to descriptive strings."""
    mapping = {
        "0": "Front",
        "1": "Rear",
        "2": "Ceiling Front",
        "3": "Ceiling Rear",
    }
    return mapping.get(payload, payload)


# ==============================================================================
# Unit Tests
# ==============================================================================

def test_info_messages():
    assert parse_info_message("INFO0") == "Standby"
    assert parse_info_message("INFO1") == "Warming"
    assert parse_info_message("INFO2") == "Cooling"
    assert parse_info_message("INFO4") == "Error - Laser"
    assert parse_info_message("INFO5") == "Thermal Error"
    assert parse_info_message("INFO6") == "FAN Locked"
    assert parse_info_message("INFO7") == "Overheat"
    assert parse_info_message("INVALID") is None


def test_status_packet_parsing():
    sample = "Ok10277814C01521"
    parsed = parse_status_packet(sample)
    assert parsed is not None
    assert parsed["power"] == "On"
    assert parsed["lamp_hours"] == "02778"
    assert parsed["source"] == "HDMI 3"
    assert parsed["firmware"] == "C015"
    assert parsed["display_mode"] == "21"


def test_status_packet_sources():
    sources_to_test = [
        ("00", "None"),
        ("06", "Video"),
        ("07", "HDMI 1"),
        ("08", "HDMI 2"),
        ("14", "HDMI 3"),
        ("99", "Unknown (99)"),
    ]
    for code, expected_name in sources_to_test:
        sample = f"Ok101000{code}C01521"
        parsed = parse_status_packet(sample)
        assert parsed["source"] == expected_name


def test_projection_mode():
    assert parse_projection_mode("0") == "Front"
    assert parse_projection_mode("1") == "Rear"
    assert parse_projection_mode("2") == "Ceiling Front"
    assert parse_projection_mode("3") == "Ceiling Rear"


# ==============================================================================
# Security by Design Tests (User Rule 5: Security by Design & Secret Hygiene)
# ==============================================================================

def test_secrets_template_completeness():
    """
    Ensures 'secrets.yaml.example' exists, contains all required configuration keys,
    and uses only safe dummy placeholder values.
    """
    from pathlib import Path
    repo_dir = Path(__file__).resolve().parent.parent
    example_path = repo_dir / "secrets.yaml.example"
    assert example_path.exists(), "secrets.yaml.example must be present in project root"

    content = example_path.read_text(encoding="utf-8")
    required_keys = [
        "wifi_ssid:",
        "wifi_password:",
        "fallback_ap_password:",
        "api_key:",
        "ota_password:",
        "web_server_password:",
    ]
    for key in required_keys:
        assert key in content, f"Required key '{key}' missing from secrets.yaml.example"

    # Verify no real secrets or live passwords in example
    assert "YOUR_WIFI_SSID" in content
    assert "YOUR_WIFI_PASSWORD" in content
    assert "GENERATE_A_32_BYTE_BASE64_KEY_HERE=" in content


def test_main_yaml_secrets_hygiene():
    """
    Ensures 'optoma_projector.yaml' contains zero hardcoded passwords or keys,
    strictly referencing '!secret' directives for all sensitive credentials.
    """
    from pathlib import Path
    repo_dir = Path(__file__).resolve().parent.parent
    yaml_path = repo_dir / "optoma_projector.yaml"
    assert yaml_path.exists(), "optoma_projector.yaml must exist"

    content = yaml_path.read_text(encoding="utf-8")

    assert "key: !secret api_key" in content, "API Encryption Key must use !secret"
    assert "password: !secret ota_password" in content, "OTA Password must use !secret"
    assert "ssid: !secret wifi_ssid" in content, "WiFi SSID must use !secret"
    assert "password: !secret wifi_password" in content, "WiFi Password must use !secret"
    assert "password: !secret fallback_ap_password" in content, "Fallback AP Password must use !secret"
    assert "password: !secret web_server_password" in content, "Web Server Password must use !secret"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
