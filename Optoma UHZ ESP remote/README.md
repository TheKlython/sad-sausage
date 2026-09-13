# 🎬 Smart Optoma Laser Projector Controller (ESP32 + RS232 + ESPHome)

A complete, enterprise-grade bi-directional RS232 serial bridge and smart controller for **Optoma home cinema projectors** (tested on Optoma UHZ2000, UHZ4000, UHD series, and compatible models) using ESPHome and an ESP32.

Replaces slow IR blasters and unreliable HDMI-CEC with direct, rock-solid serial hardware control, instant state feedback, fault detection, and seamless **Home Assistant** integration.

---

## 🌟 Key Features

- **True Power & State Feedback:** Detects exact projector phases: `Standby`, `Warming`, `On`, and `Cooling`.
- **Hardware Fault Monitoring:** Immediately catches and alerts on projector hardware faults pushed over RS232:
  - `Overheat`
  - `Fan Locked`
  - `Laser Error`
  - `Thermal Error`
  - `Out of Range`
- **Telemetry & Diagnostics:** Real-time system temperature (°C), laser/lamp hours, firmware version, input resolution (e.g. `2560x1440`), and serial number.
- **Full Picture & Mode Control:**
  - **Source Selection:** HDMI 1, HDMI 2, HDMI 3 (with active input sync).
  - **Projection Mode:** Front, Rear, Ceiling Front, Ceiling Rear.
  - **Picture Adjustments:** Sliders for Brightness (0-100) and Contrast (0-100).
  - **HDR Control:** Off / Auto.
  - **Sleep Timer:** 0 to 990 minutes in 30-minute steps.
- **Virtual D-Pad Remote:** Full on-screen menu navigation (Up, Down, Left, Right, Enter, Menu, Resync, Volume Up/Down).
- **Custom UART Terminal:** In-UI text entity to send arbitrary RS232 command strings directly from Home Assistant.
- **Smart Bus Traffic Optimization:** Uses an internal state machine (`current_query`) and caches static telemetry (serial number, projection mode) so only dynamic metrics are polled, preventing UART bus saturation.
- **Security by Design:** Encrypted Native API (Noise PSK), password-protected OTA updates, and authenticated web server.

---

## 🛠️ Hardware Requirements & Wiring

### Bill of Materials
1. **ESP32 Development Board** (NodeMCU ESP32, ESP32-WROOM-32, or D1 Mini ESP32).
2. **MAX3232 RS232-to-TTL Level Shifter Module** *(Ensure your module supports 3.3V logic levels to protect the ESP32!)*.
3. **DB9 Connector or Cable** (Male/Female depending on your projector's RS232 port).
4. **5V USB Power Supply**.

### Wiring Schematic

```
+---------------+                    +------------------+                   +------------------+
|     ESP32     |                    |     MAX3232      |                   | Optoma Projector |
|               |                    |   Transceiver    |                   |    (DB9 Port)    |
|          3.3V |------------------->| VCC              |                   |                  |
|           GND |------------------->| GND              |                   |                  |
|  GPIO 17 (TX) |------------------->| TXD / TTL IN     | RS232 TX (Pin 2)  |----------------->| Pin 2 (RX)       |
|  GPIO 16 (RX) |<-------------------| RXD / TTL OUT    | RS232 RX (Pin 3)  |<-----------------| Pin 3 (TX)       |
|               |                    |         RS232 GND|-------------------| Pin 5 (GND)      |
+---------------+                    +------------------+                   +------------------+
```

### Pinout Table

| ESP32 Pin | MAX3232 (TTL Side) | MAX3232 (RS232 Side) | Optoma DB9 Pin | Description |
| :--- | :--- | :--- | :--- | :--- |
| **3.3V** | **VCC** | - | - | Power (3.3V logic safe) |
| **GND** | **GND** | **GND** | **Pin 5** | Ground Reference |
| **GPIO 17** | **TX / T1IN** | **T1OUT** | **Pin 2 (RX)** | ESP32 Transmit $\to$ Projector Receive |
| **GPIO 16** | **RX / R1OUT** | **R1IN** | **Pin 3 (TX)** | Projector Transmit $\to$ ESP32 Receive |

> **Note on Serial Settings:** Optoma projectors communicate at `9600 Baud, 8 Data Bits, No Parity, 1 Stop Bit (8N1)` with Carriage Return (`\r` / `0x0D`) as command delimiter.

---

## ⚙️ Software Setup & Installation

### 1. Repository Structure
```
Optoma_UHZ_ESP_remote/
├── optoma_projector.yaml  # Main ESPHome firmware configuration
├── secrets.yaml.example   # Secrets template (WiFi, passwords, keys)
├── Agents.md              # Technical architecture & AI developer guide
└── tested_and_validated_commands_to_implement.md # RS232 command protocol reference
```

### 2. Configure Secrets
Copy `secrets.yaml.example` to `secrets.yaml`:
```bash
cp secrets.yaml.example secrets.yaml
```

Edit `secrets.yaml` and set your credentials:
```yaml
wifi_ssid: "YOUR_WIFI_SSID"
wifi_password: "YOUR_WIFI_PASSWORD"
fallback_ap_password: "YOUR_HOTSPOT_PASSWORD"
api_key: "GENERATE_A_32_BYTE_BASE64_KEY_HERE="
ota_password: "YOUR_SECURE_OTA_PASSWORD"
web_server_password: "YOUR_WEB_SERVER_PASSWORD"
```

To generate a secure 32-byte Base64 key for the native API:
```bash
openssl rand -base64 32
```

### 3. Flash to ESP32
- **Option A (Home Assistant ESPHome Dashboard):**
  1. Open the ESPHome dashboard in Home Assistant.
  2. Click **+ New Device**, name it `optoma-projector`.
  3. Paste the contents of [`optoma_projector.yaml`](optoma_projector.yaml).
  4. Click **Install** (via USB for the first flash, or Wirelessly / OTA subsequently).
- **Option B (ESPHome CLI):**
  ```bash
  esphome compile optoma_projector.yaml
  esphome upload optoma_projector.yaml
  ```

---

## 🧠 Architectural Insights (Why this setup is rock-solid)

Optoma projectors feature quirks in their serial protocol that make basic integrations fragile:
1. **Generic Responses:** Responses do not echo command IDs (e.g. both brightness and contrast return `Ok50`). This project uses an explicit **state machine** (`current_query`) that tracks expected replies in order.
2. **Asynchronous Push Messages:** Faults and state updates (such as `INFO2` for cooling down) are pushed unsolicited. The parser prioritizes `INFO` frames before evaluating state machine replies.
3. **Bus Traffic Minimization:** Heavy properties like serial number or firmware version are only queried once when the projector turns on, avoiding 10-second polling spam.

---

## 📱 Home Assistant Lovelace Card Example

You can combine all controls into a clean dashboard card using Mushroom or standard entities cards:

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-template-card
    primary: Optoma Projector
    secondary: "{{ states('sensor.optoma_power_state') }} | {{ states('sensor.optoma_system_temperature') }}°C"
    icon: mdi:projector
    icon_color: "{{ 'green' if is_state('sensor.optoma_power_state', 'On') else 'red' }}"
  - type: horizontal-stack
    cards:
      - type: button
        name: Power
        icon: mdi:power
        tap_action:
          action: toggle
        entity: switch.optoma_power
      - type: button
        name: AV Mute
        icon: mdi:video-off
        tap_action:
          action: toggle
        entity: switch.optoma_av_mute
      - type: button
        name: Resync
        icon: mdi:sync
        tap_action:
          action: toggle
        entity: button.optoma_resync
  - type: entities
    entities:
      - entity: select.optoma_input_source
      - entity: select.optoma_projection_mode
      - entity: number.optoma_brightness
      - entity: number.optoma_contrast
      - entity: sensor.optoma_lamp_hours
      - entity: sensor.optoma_resolution
```

---

## 🔒 Security by Design

- **Encrypted Communication:** API traffic to Home Assistant is protected using Noise PSK encryption.
- **Protected OTA:** Firmware cannot be updated over Wi-Fi without the designated `ota_password`.
- **Authenticated Local Web Server:** The fallback web interface is protected with HTTP Basic Auth.
- **Local-Only Operation:** Zero external cloud connection required; all data stays on your local LAN.

---

## 📜 License & Credits

Released under the **MIT License**. Created with ❤️ for the Home Assistant & Home Cinema community. Contributions and PRs are welcome!
