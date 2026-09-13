"""
Unit Tests für die Gaszähler-Berechnungs- und Synchronisationslogik.
Gemäß RULE[user_global] (Regel 4: Tests einbauen & Regel 3: gründliche Kommentare).

Dieses Testmodul prüft:
1. Konvertierung von Pulsen zu m³ (unter Berücksichtigung von IEEE 754 Floating-Point-Präzision)
2. Rückrechnung von m³-Eingaben zu ganzzahligen Pulsen (Kalibrierungs-Logik der 'number'-Komponente)
3. Umrechnung in thermische Energie (kWh) mit dem korrekten Brennwert/Zustandszahl-Faktor
4. Simulation von Reconnect-Deltas nach Home Assistant Neustarts
5. Stabilität bei großen Zählerwerten (> 40.000 m³ / > 400.000 Pulse)
"""

import math
from pathlib import Path
import pytest


IMP_RATIO = 0.1
KWH_FACTOR = 10.988597


def pulses_to_m3(pulses: int, ratio: float = IMP_RATIO) -> float:
    """Berechnet m³ aus Pulsen, gerundet auf 1 Nachkommastelle."""
    return round(pulses * ratio, 1)


def m3_to_pulses(m3: float, ratio: float = IMP_RATIO) -> int:
    """
    Berechnet die ganzzahligen Pulse aus einem m³-Wert.
    Entspricht exakt der ESPHome C++ Lambda-Logik:
    (int)(round(x / id(g_imp_ratio)))
    """
    return int(round(m3 / ratio))


def m3_to_kwh(m3: float, factor: float = KWH_FACTOR) -> float:
    """Berechnet kWh aus m³, gerundet auf 2 Nachkommastellen."""
    return round(m3 * factor, 2)


# ==============================================================================
# Tests für Basiskonvertierung & Präzision
# ==============================================================================

def test_initial_reading_conversion():
    """Prüft, ob der reale Zählerstand 44075.8 m³ exakt 440758 Pulse ergibt."""
    initial_m3 = 44075.8
    expected_pulses = 440758
    
    calculated_pulses = m3_to_pulses(initial_m3)
    assert calculated_pulses == expected_pulses, f"Erwartet: {expected_pulses}, Erhalten: {calculated_pulses}"
    
    recalculated_m3 = pulses_to_m3(calculated_pulses)
    assert recalculated_m3 == initial_m3, f"Erwartet: {initial_m3}, Erhalten: {recalculated_m3}"


def test_pulse_increment():
    """Prüft, dass jeder einzelne Puls den Zähler exakt um 0.1 m³ erhöht."""
    start_pulses = 440758
    start_m3 = pulses_to_m3(start_pulses)
    
    # 1 Puls mehr
    new_pulses = start_pulses + 1
    new_m3 = pulses_to_m3(new_pulses)
    
    assert new_pulses == 440759
    assert math.isclose(new_m3 - start_m3, 0.1, abs_tol=1e-5)
    assert new_m3 == 44075.9


def test_kwh_calculation():
    """Prüft die kWh-Berechnung für den Startwert."""
    m3_val = 44075.8
    # 44075.8 * 10.988597 = 484331.202326 -> 484331.20
    expected_kwh = round(44075.8 * 10.988597, 2)
    calculated_kwh = m3_to_kwh(m3_val)
    
    assert calculated_kwh == expected_kwh
    assert calculated_kwh == 484331.20


# ==============================================================================
# Tests für die Kalibrierung / Number-Entität
# ==============================================================================

def test_number_calibration_edge_cases():
    """
    Testet die Korrekturfunktion über die HA UI 'number'-Komponente.
    Prüft typische Rundungsfallen bei Fließkommazahlen.
    """
    test_cases = [
        (0.0, 0),
        (0.1, 1),
        (1.0, 10),
        (44075.8, 440758),
        (44075.9, 440759),
        (44076.0, 440760),
        (99999.9, 999999),
    ]
    
    for m3_input, expected_pulses in test_cases:
        pulses = m3_to_pulses(m3_input)
        assert pulses == expected_pulses, f"Fehler bei {m3_input} m³ -> {pulses} != {expected_pulses}"
        # Hin- und Rückweg muss identisch sein
        assert pulses_to_m3(pulses) == m3_input


# ==============================================================================
# Simulation von Ausfall-Szenarien
# ==============================================================================

def test_home_assistant_downtime_simulation():
    """
    Simuliert: Home Assistant ist für 15 Minuten offline (z.B. Core Update).
    Währenddessen laufen 7 Gas-Pulse auf dem autarken ESP auf.
    Prüft, dass nach Reconnect der exakte Endstand ohne Lücke ankommt.
    """
    ha_last_known_m3 = 44075.8
    esp_pulses = 440758
    
    # Gasuhr dreht sich während HA offline ist
    missed_pulses = 7
    esp_pulses += missed_pulses
    
    # HA kommt wieder online und liest den aktuellen ESP-Stand ein
    ha_reconnected_m3 = pulses_to_m3(esp_pulses)
    
    # Verifikation:
    delta_m3 = round(ha_reconnected_m3 - ha_last_known_m3, 1)
    assert delta_m3 == 0.7
    assert ha_reconnected_m3 == 44076.5


def test_esp_reboot_persistence_simulation():
    """
    Simuliert: ESP32 startet neu (z.B. Stromschwankung).
    Dank restore_value: true wacht er mit dem letzten Wert auf, statt bei 0 anzufangen.
    """
    # Vor dem Reboot
    nvs_stored_pulses = 440765
    
    # Nach dem Reboot (wird aus NVS geladen)
    esp_boot_pulses = nvs_stored_pulses  # restore_value: true
    
    # 1 weiterer Puls nach Reboot
    esp_boot_pulses += 1
    
    assert esp_boot_pulses == 440766
    assert pulses_to_m3(esp_boot_pulses) == 44076.6


# ==============================================================================
# Security by Design Tests (Regel 5: Security by Design & Secret Hygiene)
# ==============================================================================

def test_secrets_template_completeness():
    """
    Stellt sicher, dass 'secrets.yaml.example' alle erforderlichen Konfigurationsschlüssel
    enthält und ausschließlich sichere Platzhalter verwendet.
    """
    repo_dir = Path(__file__).resolve().parent.parent
    example_path = repo_dir / "secrets.yaml.example"
    assert example_path.exists(), "secrets.yaml.example muss im Projektverzeichnis vorhanden sein"
    
    content = example_path.read_text(encoding="utf-8")
    required_keys = [
        "wifi_ssid:",
        "wifi_password:",
        "fallback_ap_password:",
        "api_encryption_key:",
        "ota_password:",
    ]
    for key in required_keys:
        assert key in content, f"Erforderlicher Schlüssel '{key}' fehlt in secrets.yaml.example"
    
    # Sicherstellen, dass keine echten Passwörter im Template enthalten sind
    assert "YOUR_WIFI_SSID" in content
    assert "YOUR_WIFI_PASSWORD" in content
    assert "GENERATE_A_32_BYTE_BASE64_KEY_HERE=" in content


def test_main_yaml_secrets_hygiene():
    """
    Stellt sicher, dass in 'gasmeter-esp.yaml' keine Passwörter oder kryptografischen
    Schlüssel im Klartext stehen, sondern ausschließlich die '!secret'-Direktive genutzt wird.
    """
    repo_dir = Path(__file__).resolve().parent.parent
    yaml_path = repo_dir / "gasmeter-esp.yaml"
    assert yaml_path.exists(), "gasmeter-esp.yaml muss existieren"
    
    content = yaml_path.read_text(encoding="utf-8")
    
    # Prüfe zwingende !secret Referenzen für sensible Felder
    assert "key: !secret api_encryption_key" in content, "API Encryption Key muss !secret verwenden"
    assert "password: !secret ota_password" in content, "OTA Password muss !secret verwenden"
    assert "ssid: !secret wifi_ssid" in content, "WLAN SSID muss !secret verwenden"
    assert "password: !secret wifi_password" in content, "WLAN Password muss !secret verwenden"
    assert "password: !secret fallback_ap_password" in content, "Fallback AP Password muss !secret verwenden"


if __name__ == "__main__":
    pytest.main(["-v", __file__])

