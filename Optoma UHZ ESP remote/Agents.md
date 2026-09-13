# Optoma ESPHome Integration - AI Agent & Architecture Guide

This document serves as the primary technical reference and knowledge base for future iterations and AI agent maintenance on the **Optoma ESPHome Remote Integration** (Optoma UHZ2000 / UHZ4000 / UHD series via RS232 UART).

---

## 1. UART Polling State Machine (`current_query`)

Optoma projectors return generic `Ok...` responses that do not contain an echo of the command identifier they are answering.
- For example, querying brightness (`~00125 1\r`) returns `Ok50\r`, and querying contrast (`~00126 1\r`) also returns `Ok50\r`.
- **Architectural Solution:** A lightweight state machine tracks pending queries using the global integer `current_query`:
  - `0`: Idle (no query pending)
  - `1`: Status Packet (`~00150 1`)
  - `2`: System Temperature (`~00150 18`)
  - `3`: Serial Number (`~00353 1`)
  - `4`: Input Resolution (`~00150 4`)
  - `5`: Projection Mode (`~00129 1`)
  - `6`: Brightness (`~00125 1`)
  - `7`: Contrast (`~00126 1`)
- The polling script `poll_projector` sets `current_query` before writing each command, allowing the RX parser in `uart.debug` to unambiguously decode the returned payload.

---

## 2. Bus Traffic Optimization: Dynamic vs. Static Polling

Polling all projector registers every 10 seconds causes unnecessary bus saturation and prolongs the query loop.
- **Dynamic Properties:** (Power state, temperature, brightness, contrast, active input) are polled every 10 seconds.
- **Static Properties:** (Serial number, firmware version, projection orientation) are queried **only once per power cycle**.
- **Implementation:** Controlled via the global boolean `has_queried_static_info`. When the projector transitions out of `"On"`, an `on_value` trigger on `optoma_power_state` resets `has_queried_static_info` to `false`.

---

## 3. Combined Multi-Value Payloads (`~00150 1\r`)

Certain commands pack multiple telemetry data fields into a single reply string:
- Response format: `Ok<power_flag(1)><lamp_hours(5)><source(2)><firmware(4)><display_mode(2)>\r`
- **Rule:** Do not create separate polling commands for firmware version or lamp hours. They are extracted directly during status packet parsing (`current_query == 1`).

---

## 4. Asynchronous Push Messages (`INFO`)

The projector transmits unsolicited status and fault codes independently of active polling:
- `INFO0`: Standby / Off
- `INFO1`: Warming Up
- `INFO2`: Cooling Down
- `INFO4`: Laser Diode Fault
- `INFO5`: Thermal Protection Error
- `INFO6`: Fan Locked
- `INFO7`: Overheat Shutdown
- **Critical Parser Order:** The UART RX lambda must check for `INFO` message prefixes **before** evaluating standard state machine responses (`Ok`, `P`, `F`), because `INFO` messages can arrive at any arbitrary moment.

---

## 5. Security by Design

To ensure secure enterprise deployment, the configuration enforces:
- **API Encryption:** Native Home Assistant API is protected by Noise PSK (`!secret api_key`).
- **OTA Protection:** Over-The-Air firmware updates are password-protected (`!secret ota_password`).
- **Web Server Authentication:** HTTP Basic Auth protects the internal web server (`!secret web_server_password`).
- **Protected Hotspot:** The captive fallback portal uses WPA2-PSK (`!secret fallback_ap_password`).
