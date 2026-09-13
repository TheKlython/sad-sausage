# Gaszähler ESPHome Integration - AI Agent Dokumentation & Wissensdatenbank

Dieses Dokument dient als Wissensdatenbank und Leitfaden für zukünftige Iterationen und Anpassungen an der Gaszähler-Integration (`Gasmeter_ESP`). Bitte lies diese Dokumentation, bevor Du Änderungen am Code vornimmst.

---

## 1. Hardware & Pulserfassung

- **Messprinzip:** Ein optischer Reflexkoppler (oder Hallsensor) tastet die letzte Ziffernrolle des Gaszählers ab (z.B. Reflexspiegel bei der Ziffer 0).
- **Pin 33 (ADC):** Der ESP32 misst über den ADC-Kanal das analoge Spannungssignal (`GasMeterAnalogInput`, 12dB Attenuation).
- **Analog Threshold:** Der `binary_sensor` (`GasMeterAnalogTreshhold`) schaltet bei Über-/Unterschreiten des Schwellenbereichs (1.59V – 1.62V).
- **Inkrementierung:** Der Puls wird bei `on_release` gezählt (`id(total_pulses2) += 1;`).
- **Wertigkeit:** $1\,\text{Puls} = 0{,}1\,\text{m}^3$ Gas (`imp_ratio: 0.1`).

---

## 2. Zählerführung & Ausfallsicherheit (Option 1)

### NVS-Flash-Persistenz (`restore_value: true`)
- Im Urzustand war `restore_value: false` konfiguriert, wodurch der ESP bei jedem Neustart (OTA, Stromunterbrechung, WiFi-Timeout) den Zählerstand verlor und bei 0 begann.
- **Lösung:** `total_pulses2` ist als `restore_value: true` definiert (initialer Startwert per Substitution oder `0`). Der Zählerstand wird anschließend bequem über die Home Assistant Oberfläche kalibriert.
- **Wear-Leveling:** ESPHome nutzt das nichtflüchtige Speichersystem (NVS) des ESP-IDF mit integriertem Wear-Leveling. Geänderte Werte werden schonend in rotierende Sektoren geschrieben, sodass kein Flash-Verschleiß bei normaler Gasfluss-Frequenz droht.

### Verhalten bei Home Assistant Neustarts (Downtime)
- Der ESP32 zählt im laufenden Betrieb autark.
- Fällt Home Assistant wegen Updates oder Wartung für 15–30 Minuten aus, werden alle Zwischenimpulse im RAM und NVS des ESP akkumuliert.
- Sobald Home Assistant wieder hochfährt und die Native API Verbindung herstellt, empfängt HA den neuen Gesamtzählerstand. **Kein einziger Puls geht verloren.**

---

## 3. Realtime Push statt Polling

- Im Standard-Template-Sensor von ESPHome wird der Wert nur zyklisch (z.B. alle 60 Sekunden) aktualisiert.
- **Problem:** Automatisierungen in Home Assistant (wie `automation.gaszahler_puls_notify_alexa`, die bei Gasfluss sofort einen Signalton abspielt) würden mit bis zu 60 Sekunden Verzögerung auslösen.
- **Best Practice / Implementiert:**
  Direkt in der `on_release`-Aktion des `binary_sensor` werden die neuen Sensorwerte sofort via `publish_state(...)` an die Native API gesendet:
  ```cpp
  id(total_pulses2) += 1;
  float current_m3 = id(total_pulses2) * id(g_imp_ratio);
  float current_kwh = current_m3 * id(g_kwh_factor);

  id(gas_zaehlerstand).publish_state(current_m3);
  id(gas_verbrauch_ad).publish_state(current_m3);
  id(gas_kwh).publish_state(current_kwh);
  ```

---

## 4. Home Assistant Kompatibilität & Counter-Limitation

- **Warum kein HA `counter`?**
  Der Home Assistant Helfer `counter` (`counter.gas_zaehlerstand`) akzeptiert ausschließlich **ganze Zahlen (Integers)**. Er kann keine Kommastellen wie `44075,8` abbilden.
- **Sensor-Architektur:**
  Home Assistant verlangt für das **Energie-Dashboard** Sensoren mit:
  - `device_class: gas`
  - `state_class: total_increasing`
  - `unit_of_measurement: "m³"`
  Der vom ESP bereitgestellte Sensor `sensor.gasmeter_esp_gasverbrauchpuls` (oder `GasverbrauchPuls`) erfüllt diese Spezifikation zu 100% und kann direkt im Energie-Dashboard eingebunden werden.

---

## 5. Kalibrierungs-Schnittstelle (`number.template`)

- Um den Zählerstand bei Abweichungen, Zählertausch oder manueller Ablesung anzupassen, ist eine `number`-Komponente implementiert:
  - Entität in HA: `number.gasmeter_esp_gaszahler_stand_korrektur`
  - Modus: `box` (direkte Zifferneingabe mit Kommastelle)
  - Schrittweite: `0.1 m³`
- Beim Ändern des Werts in Home Assistant rechnet die `set_action` den m³-Wert in Pulse um, schreibt `total_pulses2` neu und pusht alle Sensoren sofort.

---

## 6. Security by Design

- **API Encryption:** Die Verbindung zu Home Assistant erfolgt verschlüsselt über Noise PSK (`key: !secret api_encryption_key` aus `secrets.yaml`).
- **OTA Authentifizierung:** Over-the-Air Firmware-Updates sind durch ein Passwort abgesichert.
- **Fallback AP:** Für den Verbindungsverlust ist ein WPA2-gesicherter Notfall-Hotspot eingerichtet.
