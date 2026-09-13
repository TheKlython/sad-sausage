# 🧯 Outage-Resilient Smart Gas Meter Tracker (ESP32 + ESPHome)

An enterprise-grade, outage-resilient pulse tracker for mechanical diaphragm gas meters using ESPHome, ESP32, and an optical or magnetic sensor.

Built specifically to solve the common pitfalls of smart gas metering in **Home Assistant**, such as lost pulses during Home Assistant updates, counter resets after ESP power loss, integer limitations of Home Assistant helpers, and sudden multi-thousand cubic meter spikes in the Energy Dashboard.

---

## 🎯 Key Problems Solved

| Common Smart Meter Problem | How This Project Solves It |
| :--- | :--- |
| **Lost Pulses during Home Assistant Updates** | The ESP32 tracks pulses autonomously. If Home Assistant is offline for minutes or hours (updates, restarts, maintenance), the ESP continues accumulating pulses in hardware. Once Home Assistant reconnects, the new cumulative total is immediately synchronized without losing a single pulse. |
| **ESP32 Reboots Reset Counter to 0** | The total pulse count is stored in ESP-IDF **Non-Volatile Storage (NVS Flash)** with `restore_value: true`. The ESP resumes from its exact last reading after power outages or OTA updates. ESP-IDF handles flash wear-leveling automatically. |
| **HA `counter` Decimal Limitation** | Home Assistant's built-in `counter` helper is restricted to integers and cannot store decimal readings (e.g. `44075.8 m³`). This project publishes native float sensors with `state_class: total_increasing` directly compatible with the HA Energy Dashboard. |
| **Energy Dashboard Spikes** | Switching an existing counter to the real meter reading often causes Home Assistant to record a massive one-time consumption spike (e.g. 40,000 m³ in a single hour). This guide documents how to prevent and instantly eliminate any historical rollup spikes using Home Assistant's statistics API. |
| **Delayed Notification Triggers** | Standard template sensors poll on interval (e.g. 60s). This setup pushes state changes **immediately** on pulse release, triggering real-time automations (such as Alexa chimes or burner flame alerts) with zero delay. |

---

## 📐 Architecture Overview

```
                          +----------------------------------------------+
                          |                 ESP32 Node                   |
                          |                                              |
[Gas Meter Dial] -------->| GPIO 33 (ADC) -> Analog Threshold Detector   |
 (Reflective Spot)        |    │                                         |
                          |    ▼ On Pulse Release (+1)                   |
                          | Non-Volatile Flash Counter (NVS Persistent)  |
                          |    │                                         |
                          |    ├─► sensor.gas_meter_reading (m³)         |
                          |    ├─► sensor.gas_meter_kwh (kWh)            |
                          |    └─► number.gas_meter_correction           |
                          +----------------------┬-----------------------+
                                                 │ Native API (Encrypted)
                                                 ▼
                          +----------------------------------------------+
                          |                Home Assistant                |
                          |                                              |
                          |  - Energy Dashboard (Native Gas Source)      |
                          |  - Real-time Automations & Notifications     |
                          |  - In-UI Meter Calibration Card              |
                          +----------------------------------------------+
```

---

## 🛠️ Hardware Requirements & Wiring

### Bill of Materials
- **Microcontroller:** ESP32 development board (e.g. ESP32-WROOM-32 / NodeMCU ESP32)
- **Pulse Sensor (Reference Setup):** 
  - **Primary / Reference Sensor:** **OH49E Linear Hall-Effect Sensor** (tested and highly reliable for gas meters with an integrated magnet in the rotating dial wheel; detects continuous micro-deflections in analog voltage).
  - **Alternative (Optical):** TCRT5000 infrared reflective sensor module (for dials with a reflective mirror on the '0' digit).
  - **Alternative (Digital Switch):** Reed contact or KY-024 / KY-035 Hall module.
- **Power Supply:** 5V USB power supply (or rechargeable battery with UPS buffer).

### Pin Wiring

| Sensor Pin | ESP32 Pin | Description |
| :--- | :--- | :--- |
| **VCC** | **3.3V** (or 5V) | Power supply (3.3V recommended for direct ADC level matching) |
| **GND** | **GND** | Common Ground |
| **AO / OUT** | **GPIO 33** | Analog Output connected to ESP32 ADC1 Channel 5 |

> **Note on ADC Pin Choice:** On ESP32, ADC2 pins cannot be used reliably when Wi-Fi is active. **GPIO 33 belongs to ADC1**, which remains fully functional while Wi-Fi is connected.

---

### 📸 Reference Hardware Setup

Below is the reference hardware installation of the **OH49E linear Hall sensor** mounted directly on the gas meter dial housing:

![OH49E Gas Meter Setup](setup.jpg)

*(Place your own installation photo as `setup.jpg` in this directory to showcase your setup).*

---

### 🎯 Calibrating Analog Voltage Thresholds (OH49E Hall Sensor)

Because magnet strength, physical mounting distance, plastic housing thickness, and supply voltage vary between meter models, **the threshold voltages in [`gasmeter-esp.yaml`](gasmeter-esp.yaml) must be calibrated to your installation**:

```yaml
binary_sensor:
  - platform: analog_threshold
    name: "GasMeterAnalogTreshhold"
    sensor_id: gasmeteranaloginput
    threshold:
      upper: 1.62   # <--- Calibrate to your idle baseline
      lower: 1.59   # <--- Calibrate to your deflection trigger
```

#### Step-by-Step Calibration:
1. **Flash firmware and monitor sensor voltage:**  
   Open the ESPHome web dashboard, Home Assistant developer tools, or the ESPHome CLI log viewer:
   ```bash
   esphome logs gasmeter-esp.yaml
   ```
2. **Determine Idle Baseline Voltage ($V_{\text{idle}}$):**  
   While no gas is flowing and the dial magnet is away from the sensor, note the reading of `GasMeterAnalogInput` (e.g. `~1.65V`).
3. **Determine Deflection Voltage ($V_{\text{pulse}}$):**  
   Turn on a gas burner or wait for gas flow. As the magnet passes the OH49E sensor, the voltage will noticeably swing (e.g. dipping to `~1.55V` or rising depending on magnetic pole orientation).
4. **Set Hysteresis Thresholds (Schmitt Trigger):**  
   Configure `upper` and `lower` to sit cleanly between your idle baseline and the deflection peak. A typical hysteresis band of **20–30 mV** ensures instant, bounce-free triggering without missing pulses or registering false counts.

---

## ⚙️ Software Configuration

### 1. File Structure
```
Gasmeter_ESP/
├── gasmeter-esp.yaml       # Main ESPHome configuration
├── secrets.yaml.example    # Credentials template (WiFi, API keys, OTA password)
├── Agents.md               # AI Agent & Architecture documentation
└── tests/
    └── test_gasmeter.py    # Automated unit tests for calculation precision & deltas
```

### 2. Configure Secrets
Copy `secrets.yaml.example` to `secrets.yaml`:
```bash
cp secrets.yaml.example secrets.yaml
```
Fill in your Wi-Fi credentials and generate a strong 32-byte Base64 key for the native API:
```bash
openssl rand -base64 32
```

### 3. Adjust Substitutions in `gasmeter-esp.yaml`
Edit the `substitutions` block at the top of [`gasmeter-esp.yaml`](gasmeter-esp.yaml):
```yaml
substitutions:
  name: "gasmeter-esp"
  friendly_name: "Gas Meter ESP"

  # Initial reading in pulses (or leave "0" and set via Home Assistant UI!)
  # Calculation: (Current reading on meter dial) / (imp_ratio)
  # Example: 44075.8 m³ / 0.1 m³/pulse = 440758 pulses
  initial_pulses: "0"

  # Pulse ratio of your meter:
  # 1 pulse = 0.1 m³ (common for BK-G4 / Pipersberg / Elster meters)
  imp_ratio: "0.1"

  # Calorific value * Z-number from your utility bill (e.g. ~10.2 to ~11.5 kWh/m³)
  kwh_factor: "10.988597"
```

---

## 🚀 Deployment

1. **Via Home Assistant ESPHome Dashboard (Easiest):**
   - In Home Assistant, navigate to **ESPHome Device Builder**.
   - Click **+ New Device** or edit your existing device.
   - Paste the contents of [`gasmeter-esp.yaml`](gasmeter-esp.yaml).
   - Click **Save** and **Install** (Wirelessly / OTA or via USB).

2. **Via ESPHome CLI:**
   ```bash
   esphome compile gasmeter-esp.yaml
   esphome upload gasmeter-esp.yaml
   ```

---

## 🎛️ Calibration & Home Assistant Integration

### 1. In-UI Meter Reading Calibration
Once flashed, ESPHome creates a `number` entity in Home Assistant:
- **Entity:** `number.gasmeter_esp_gaszahler_stand_korrektur`
- **UI Mode:** Box (direct decimal numeric input)

Whenever you read your physical meter or perform an annual check:
1. Open Home Assistant.
2. Enter the current dial reading (e.g. `44075.8`).
3. The ESP32 recalculates the exact pulse count, writes it directly to NVS flash, and synchronizes all sensors immediately. No firmware recompilation required!

### 2. Home Assistant Energy Dashboard Setup
1. Go to **Settings** -> **Dashboards** -> **Energy**.
2. Under **Gas Consumption**, click **Add Gas Source**.
3. Select `sensor.gasmeter_esp_gasverbrauchpuls` (GasverbrauchPuls).
4. If you have gas price tracking, select your price entity or enter your fixed gas tariff.

---

## 🛡️ Avoiding & Fixing Energy Dashboard Spikes

### Why Do Spikes Happen?
If a sensor transitions from a small number (or `0.5 m³`) to your real cumulative reading (e.g. `44075.8 m³`), Home Assistant's statistics engine may calculate the difference as a massive single-hour consumption:
$$\Delta = 44075.8\,\text{m}^3 - 0.5\,\text{m}^3 = 44075.3\,\text{m}^3$$

### How to Fix / Remove the Spike:
If an unexpected spike appears in your Energy Dashboard:
1. In Home Assistant, open **Developer Tools** (`Entwicklerwerkzeuge`).
2. Switch to the **Statistics** (`Statistik`) tab.
3. Search for `gasverbrauchpuls`.
4. Click the ramp/chart icon on the far right (**Adjust Statistics** / *Messfehler korrigieren*).
5. Select the 5-minute interval where the jump occurred and enter the negative offset (e.g. `-44075.30 m³`).
6. The historical statistics sum is corrected instantly, and the single-hour spike vanishes completely from your Energy Dashboard!

---

## 🧪 Automated Testing

A dedicated test suite using `pytest` is included in [`tests/test_gasmeter.py`](tests/test_gasmeter.py). It validates:
- IEEE 754 floating-point conversion accuracy between pulses and $m^3$.
- Inversion calculation for the calibration entity without off-by-one errors.
- Energy conversion ($m^3 \to \text{kWh}$).
- Outage delta recovery (simulating 15 minutes of Home Assistant downtime while pulses accumulate).
- ESP reboot persistence simulation.
- Automated secret hygiene and template completeness.

Run the test suite locally:
```bash
python -m pytest tests/test_gasmeter.py -v
```

---

## 🔒 Security by Design

- **Encrypted API:** The ESP32 connects to Home Assistant using the native API protected with modern **Noise PSK** cryptography (`api_encryption_key`).
- **Protected OTA:** Firmware updates over the air require an authentication password (`ota_password`).
- **Captive Hotspot:** The fallback hotspot is secured with WPA2-PSK and only triggers if the configured Wi-Fi is persistently unreachable.
- **Web Server Protection:** The embedded diagnostic web server can be password-protected via ESPHome's `auth` component or disabled entirely on sensitive networks.
- **Zero Cloud Dependency:** Operates 100% locally on your local network.

---

## 📜 License & Credits

Distributed under the MIT License as part of the [Sad Sausage (SS-Ops)](../README.md) open-source Edge AI & Smart-Home ecosystem.
Created with ❤️ for the Home Assistant & ESPHome DIY community.
Feel free to share, fork, and contribute!
