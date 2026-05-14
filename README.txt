===============================================================================
              USB-RELAY04 Control Tool  -  User Guide
              HW-34 / USB-RELAY04  (4-channel USB relay board)
===============================================================================

This package provides three ways to control a USB-RELAY04 board:

  1. GUI application     (full graphical interface)
  2. System-tray app     (quick ON/OFF from the Windows notification area)
  3. Command-line tool   (scripting and automation)

All three share the same configuration file (relay_mapping.cfg).


===============================================================================
  CONTENTS
===============================================================================

  1. Requirements
  2. Driver Installation
  3. Configuration  (relay_mapping.cfg)
  4. GUI Application
  5. System Tray App
  6. Command-Line Interface (CLI)
  7. Auto-Start on Windows Boot
  8. Troubleshooting
  9. File Overview


===============================================================================
  1. REQUIREMENTS
===============================================================================

  - Windows 10 or later (64-bit)
  - Python 3.8 or later
  - PL2303 USB-to-Serial driver (included in the Driver folder)

  Python packages (installed automatically by start_gui.bat or manually):

    pyserial   - Serial port communication
    tk         - GUI toolkit (usually bundled with Python)
    pystray    - System tray icon support
    Pillow     - Image/icon generation (dependency of the GUI and tray app)
    customtkinter - Modern themed GUI widgets

  To install all packages manually, run:

    pip install -r requirements.txt


===============================================================================
  2. DRIVER INSTALLATION
===============================================================================

  The relay board uses a PL2303 USB-to-Serial chip.

  Steps:
    1. Navigate to the "Driver\PL2303_DriverInstaller(x64bits)" folder.
    2. Extract the archive if needed.
    3. Right-click the installer and choose "Run as administrator".
    4. Follow the on-screen prompts.
    5. Plug in the relay board via USB.
    6. Open Device Manager and note the assigned COM port (e.g. COM3).


===============================================================================
  3. CONFIGURATION  (relay_mapping.cfg)
===============================================================================

  All tools read settings from "relay_mapping.cfg" in the project folder.
  Edit this file with any text editor.

  ---------- relay_mapping.cfg ----------

  [SerialPort]
  port = COM3                     <-- Set this to your relay's COM port

  [Relays]
  relay1label = PSU 1 Control     <-- Custom label for Relay 1
  relay2label = PSU 2 Control     <-- Custom label for Relay 2
  relay3label = Motor Control     <-- Custom label for Relay 3
  relay4label = CAN Short to GND  <-- Custom label for Relay 4

  [UI]
  theme = Dark                    <-- Light | Dark | System
  auto_refresh_ports = 1          <-- 1 = auto-detect new COM ports, 0 = off
  ports_refresh_ms = 3000         <-- How often to scan for ports (ms)

  ----------------------------------------

  Tip: The GUI will save the last-used COM port and theme back into this file
       automatically, so you usually only need to edit it once.


===============================================================================
  4. GUI APPLICATION
===============================================================================

  Start:
    Double-click "start_gui.bat"
    (This checks/installs Python dependencies, then opens the GUI.)

  Features:
    - COM port selector      Pick from all available serial ports. The
                             dropdown auto-refreshes every few seconds.

    - Connect / Disconnect   Opens or closes the serial connection.
                             Status badge shows CONNECTED (green) or
                             DISCONNECTED (red).

    - 4 Relay cards          Each card shows the relay number, its custom
                             label (from config), an ON/OFF pill badge, and
                             a toggle switch. Flip the switch to control
                             that individual relay.

    - ALL ON button          Turns all four relays on at once (green).

    - ALL OFF button         Turns all four relays off at once (red).

    - Always-on-top toggle   Keeps the window above all other windows.

    - Dark / Light theme     Switches the UI theme instantly and saves the
                             preference to the config file.

    - Log panel              Shows all serial communication, connection
                             events, and relay state changes.

  Typical workflow:
    1. Run start_gui.bat.
    2. Select the correct COM port from the dropdown.
    3. Click "Connect".
    4. Use the individual switches or ALL ON / ALL OFF buttons.
    5. Close the window when done (serial port is released automatically).


===============================================================================
  5. SYSTEM TRAY APP
===============================================================================

  A lightweight tool that sits in the Windows notification area (system tray,
  bottom-right corner near the clock) and gives instant relay control without
  opening a full window.

  Start:
    Double-click "start_tray.bat"
    (Runs in the background with no console window.)

  Controls:

    LEFT-CLICK the tray icon
      -> Toggles all relays ON <-> OFF.
         First click turns everything ON, next click turns everything OFF,
         and so on.

    RIGHT-CLICK the tray icon
      -> Opens a context menu:

         "ALL ON"             Turn all 4 relays on.
         "ALL OFF"            Turn all 4 relays off.
         "Port: COMx"         Shows which port is being used (read-only).
         "Exit"               Closes the tray app and releases the port.

  Tray icon colours:
    Green circle   = All relays are ON
    Red circle     = All relays are OFF
    Amber circle   = Idle (just started, no command sent yet)

  Hover over the icon to see the current state as a tooltip.

  Notes:
    - The tray app reads the COM port from relay_mapping.cfg.
    - The serial connection is kept open for instant response (no lag).
    - If the USB cable is disconnected, it will automatically reconnect
      on the next click.
    - You can run the tray app and the GUI at the same time, but they
      should NOT be connected to the same COM port simultaneously.


===============================================================================
  6. COMMAND-LINE INTERFACE (CLI)
===============================================================================

  File: usb_relay_hw34_cli.py

  NOTE: The CLI uses the COM port hardcoded at the top of the script.
        Open usb_relay_hw34_cli.py and change the line:
          ser = serial.Serial('COM10', ...)
        to match your COM port before first use.

  Commands:

    Initialize the relay (required once after power-on):
      python usb_relay_hw34_cli.py --init

    Turn on specific relays (1-4):
      python usb_relay_hw34_cli.py --init --on 1
      python usb_relay_hw34_cli.py --init --on 1 2 3 4

    Turn off specific relays:
      python usb_relay_hw34_cli.py --init --off 3

    Combine on and off:
      python usb_relay_hw34_cli.py --init --on 1 2 --off 3 4

  Arguments:
    --init        Initialize relay handshake (recommended every run)
    --on N [N..]  Turn on relay(s) numbered 1 through 4
    --off N [N..] Turn off relay(s) numbered 1 through 4

  Example - turn on relays 1 and 2, turn off relays 3 and 4:
    python usb_relay_hw34_cli.py --init --on 1 2 --off 3 4


===============================================================================
  7. AUTO-START ON WINDOWS BOOT
===============================================================================

  To have the tray app always available after login:

    1. Press  Win + R  on your keyboard.
    2. Type   shell:startup   and press Enter.
       (This opens your personal Startup folder.)
    3. Right-click inside the folder -> New -> Shortcut.
    4. Browse to "start_tray.bat" in the usb-relay004 folder.
    5. Click Next, give it a name (e.g. "USB Relay Tray"), click Finish.

  From now on, every time you log in, the relay tray icon will appear
  automatically in your notification area.

  To remove it, simply delete the shortcut from the Startup folder.


===============================================================================
  8. TROUBLESHOOTING
===============================================================================

  Problem: "No serial ports found" or wrong COM port
    - Open Device Manager -> Ports (COM & LPT).
    - Check which COMx is assigned to "Prolific PL2303".
    - Update relay_mapping.cfg with the correct port.
    - For the CLI, also update the port in usb_relay_hw34_cli.py.

  Problem: Driver not working / "Code 10" error
    - Uninstall the PL2303 driver from Device Manager.
    - Re-install using the driver in the Driver folder (run as admin).
    - Try a different USB port or cable.

  Problem: Relay does not respond after connect
    - The relay board needs a 1-second initialization handshake.
      The GUI and tray app handle this automatically.
    - For the CLI, always include --init on the first run.

  Problem: Tray icon not visible
    - Windows may hide new tray icons. Click the "^" arrow in the
      notification area to see hidden icons.
    - To pin it: Settings -> Personalization -> Taskbar ->
      Other system tray icons -> enable "USB-RELAY04".

  Problem: "ModuleNotFoundError: No module named 'pystray'"
    - Run:  pip install pystray
    - Or:   pip install -r requirements.txt

  Problem: GUI buttons are greyed out
    - You must connect first. Select a COM port and click "Connect".


===============================================================================
  9. FILE OVERVIEW
===============================================================================

  start_gui.bat              Launch the GUI (checks dependencies first)
  start_tray.bat             Launch the system tray app (no console window)

  usb_relay_hw34_gui.py      Full GUI application (CustomTkinter)
  usb_relay_hw34_cli.py      Command-line interface
  relay_tray.py              System tray quick-control app

  relay_mapping.cfg          Shared configuration (COM port, labels, theme)
  requirements.txt           Python package list
  check_requirements.py      Auto-installs missing Python packages

  README.txt                 This file
  README.md                  Short markdown readme (for GitHub/repository)

  Driver/                    PL2303 USB-to-Serial driver installer


===============================================================================
