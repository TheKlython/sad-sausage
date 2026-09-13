# Optoma RS232 Command Protocol Reference

This reference documents tested and validated RS232 serial commands for Optoma projectors (tested on Optoma UHZ2000 / UHZ4000 / UHD series).

Communication Parameters: `9600 Baud, 8 Data Bits, No Parity, 1 Stop Bit (8N1)`, delimiter: `\r` (ASCII 0x0D).

---

## 1. Query / Read Commands
*(Note: Most queries only respond when the projector is powered ON)*

| Command | Description | Example Response | Format & Notes |
| :--- | :--- | :--- | :--- |
| `~00150 1\r` | Comprehensive Status | `Ok10277814C01521\r` | `Ok<power(1)><lamp_hours(5)><source(2)><firmware(4)><display_mode(2)>` |
| `~00353 1\r` | Serial Number | `OkQ7JL213KAAAEC0491\r` | `Ok<Serial_Number_String>` |
| `~00150 4\r` | Input Resolution | `Ok2560x1440\r` | `Ok<Width>x<Height>` |
| `~00129 1\r` | Projection Mode | `Ok2\r` | `0` = Front, `1` = Rear, `2` = Ceiling Front, `3` = Ceiling Rear |
| `~00125 1\r` | Brightness Level | `Ok50\r` | `Ok<0-100>` |
| `~00126 1\r` | Contrast Level | `Ok50\r` | `Ok<0-100>` |
| `~00150 18\r` | System Temperature | `Ok32.5\r` | `Ok<temperature_celsius>` |

---

## 2. Control / Write Commands
*(Acknowledge response on success: `P\r`, on error / unrecognized: `F\r` or timeout)*

| Command | Function | Values / Parameters |
| :--- | :--- | :--- |
| `~0000 1\r` | Power ON | Turn projector ON |
| `~0000 2\r` | Power OFF | Turn projector OFF / Standby |
| `~0002 1\r` / `~0002 2\r` | AV Mute | `1` = Mute Video/Audio, `2` = Unmute |
| `~0003 1\r` / `~0003 2\r` | Audio Mute | `1` = Mute Audio, `2` = Unmute |
| `~0012 1\r` | Input Source HDMI 1 | Switch to HDMI 1 |
| `~0012 15\r` | Input Source HDMI 2 | Switch to HDMI 2 |
| `~0012 16\r` | Input Source HDMI 3 | Switch to HDMI 3 |
| `~0071 <mode>\r` | Set Projection Mode | `0` = Front, `1` = Rear, `2` = Ceiling Front, `3` = Ceiling Rear |
| `~0021 <0-100>\r` | Set Brightness | Value between 0 and 100 |
| `~0022 <0-100>\r` | Set Contrast | Value between 0 and 100 |
| `~00565 <0/1>\r` | Set HDR Mode | `0` = Off, `1` = Auto |
| `~00107 <min>\r` | Set Sleep Timer | Minutes (0-990 in 30 min increments, e.g. `~00107 150\r` for 150 min) |
| `~0001 1\r` | Resync Video Signal | Triggers input resync |
| `~00140 10\r` | Key: Up | D-Pad Up |
| `~00140 14\r` | Key: Down | D-Pad Down |
| `~00140 11\r` | Key: Left | D-Pad Left |
| `~00140 13\r` | Key: Right | D-Pad Right |
| `~00140 12\r` | Key: Enter | Confirm / Select |
| `~00140 20\r` | Key: Menu | Open On-Screen Display Menu |
| `~00140 18\r` | Key: Volume Up | Increase Volume |
| `~00140 17\r` | Key: Volume Down | Decrease Volume |

---

## 3. Asynchronous Projector Push Messages (`INFO`)
The projector sends unsolicited status packets on state changes:

| Message | Meaning / State |
| :--- | :--- |
| `INFO0` | Projector is in Standby / OFF |
| `INFO1` | Projector is Warming Up / Starting |
| `INFO2` | Projector is Cooling Down |
| `INFO3` | Source Signal Out of Range |
| `INFO4` | Error - Laser Diode Failure |
| `INFO5` | Thermal Error / Temperature Critical |
| `INFO6` | FAN Locked / Cooling Fan Failure |
| `INFO7` | Overheat Shutdown |

---

## 4. Response Acknowledgment Codes

- `P\r` : Command accepted and processed.
- `F\r` : Command failed or parameter invalid.
