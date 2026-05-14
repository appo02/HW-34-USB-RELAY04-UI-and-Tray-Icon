# HW-34 USB-RELAY04 — Control Suite

> Full-featured Windows control tool for the **HW-34 / USB-RELAY04** 4-channel USB relay board (seeit.fr).  
> GUI · System Tray · CLI — pick whatever fits your workflow.

---

## What Is This?

The HW-34 (USB-RELAY04) is a 4-channel relay module that connects to your PC via USB using a PL2303 serial chip. This project gives you **three ways** to control it:

| Tool | Launch | Best For |
|------|--------|----------|
| **GUI** | `start_gui.bat` | Full control — per-relay switches, labels, status, logging |
| **System Tray** | `start_tray.bat` | Quick toggle — lives in your notification area, always one click away |
| **CLI** | `python usb_relay_hw34_cli.py` | Scripting & automation — batch files, CI pipelines, test rigs |

All three tools share a single config file (`relay_mapping.cfg`) for COM port and relay labels.

---

## Features

- **Modern GUI** — Dark/Light theme, auto-detect COM ports, per-relay toggle switches, ALL ON / ALL OFF, always-on-top mode, real-time log panel
- **System Tray Quick-Control** — Left-click to toggle all relays ON↔OFF, right-click menu for individual actions, colour-coded icon (green/red/amber)
- **Command-Line Interface** — Initialize, turn on/off individual or multiple relays with a single command
- **Persistent Configuration** — COM port, relay labels, and UI preferences saved to `relay_mapping.cfg`
- **Auto-Reconnect** — Tray app keeps the serial port open for instant response; reconnects automatically if USB is unplugged
- **Zero External Images** — All icons are generated in code (PIL), no image files needed

---

## Hardware

- **Board:** HW-34 / USB-RELAY04 (4-channel, seeit.fr)
- **Chip:** PL2303 USB-to-Serial
- **Protocol:** 9600 baud, 8N1, single-byte relay state commands
- **Relay Logic:** Bit cleared = relay ON, bit set = relay OFF (low nibble, bits 0–3)

---

## Installation

### 1. Install the PL2303 Driver

1. Navigate to `Driver/PL2303_DriverInstaller(x64bits)/`.
2. Run the installer **as Administrator**.
3. Plug in the relay board and note the COM port in Device Manager.

### 2. Install Python Dependencies

```sh
pip install -r requirements.txt
```

Or simply run `start_gui.bat` — it auto-installs missing packages.

### 3. Configure

Edit `relay_mapping.cfg`:

```ini
[SerialPort]
port = COM3

[Relays]
relay1label = PSU 1 Control
relay2label = PSU 2 Control
relay3label = Motor Control
relay4label = CAN Short to Ground

[UI]
theme = Dark
auto_refresh_ports = 1
ports_refresh_ms = 3000
```

---

## Usage

### GUI Application

```
start_gui.bat
```

1. Select your COM port from the dropdown.
2. Click **Connect**.
3. Use the per-relay switches or **ALL ON** / **ALL OFF** buttons.
4. Close the window to disconnect.

### System Tray App

```
start_tray.bat
```

- **Left-click** the tray icon → toggle all relays ON ↔ OFF.
- **Right-click** → menu with ALL ON, ALL OFF, port info, Exit.
- Icon colour: 🟢 all ON · 🔴 all OFF · 🟡 idle.

**Auto-start on boot:** press `Win+R`, type `shell:startup`, drop a shortcut to `start_tray.bat` in that folder.

### Command-Line Interface

```sh
# Initialize + turn on relays 1 and 2
python usb_relay_hw34_cli.py --init --on 1 2

# Turn off relay 3
python usb_relay_hw34_cli.py --init --off 3

# Combine
python usb_relay_hw34_cli.py --init --on 1 2 --off 3 4
```

> **Note:** The CLI has the COM port hardcoded at the top of `usb_relay_hw34_cli.py`. Update it to match your setup.

---

## Project Structure

```
start_gui.bat              Launch GUI (auto-installs deps)
start_tray.bat             Launch system tray app (background)
usb_relay_hw34_gui.py      Full GUI application (CustomTkinter)
usb_relay_hw34_cli.py      Command-line interface
relay_tray.py              System tray quick-control
relay_mapping.cfg          Shared configuration
requirements.txt           Python dependencies
check_requirements.py      Dependency auto-installer
Driver/                    PL2303 USB-to-Serial driver
```

---

## Requirements

- Windows 10+ (64-bit)
- Python 3.8+
- `pyserial`, `customtkinter`, `Pillow`, `pystray`

---

## License

Free to use for personal and project work.
