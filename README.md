# usb-relay004

Control application for USB-RELAY04 (seeit.fr)
![image](https://github-vni.geo.conti.de/storage/user/20685/files/034a47e2-028f-41c8-ad8e-5f8cd27c7d88)


## Installation

1. **Extract and Install Driver:**
   - Extract and run as administrator the driver installer located at `usb-relay004\PL2303_DriverInstaller(x64bits).7z`.

2. **Configure Relay Mapping:**
   - Adapt the corresponding local configuration in the config file `usb-relay004\relay_mapping.cfg`.

3. **Start the GUI Application:**
   - Run `start_gui.bat` (this will check the Python requirements and start the GUI app).

## Usage

### GUI Application

The GUI application allows you to control the relays via a graphical interface.

- **Start the GUI:**
  - Run `start_gui.bat`.

- **Toggle Relays:**
  - Use the buttons in the GUI to toggle the relays on and off.

### Command Line Interface (CLI)

The CLI application allows you to control the relays via command line as in example below.

- **Initialize the Relay:**
  ```sh
  python usb_relay_hw34_cli.py --init
- **Control the Relay:**
  ```sh
  python usb_relay_hw34_cli.py --on 1
  python usb_relay_hw34_cli.py --off 1
  python usb_relay_hw34_cli.py --on 1 2 3
