===============================================================================
        USB-RELAY04 Control Suite  -  Installer Guide
        Version 1.0.0
===============================================================================

  This installer sets up the USB-RELAY04 Control Suite on any Windows PC.
  No Python or other dependencies are required — everything is included.


===============================================================================
  WHAT GETS INSTALLED
===============================================================================

  USB-RELAY04 GUI          Full graphical control panel with per-relay
                           switches, dark/light theme, auto-detect COM
                           ports, logging, and always-on-top mode.

  USB-RELAY04 Tray         Lightweight system tray icon that lives in
                           your notification area (bottom-right, near
                           the clock). Left-click to toggle all relays
                           ON/OFF instantly. Right-click for menu.

  USB-RELAY04 CLI          Command-line tool for scripting and automation.

  PL2303 Driver            USB-to-Serial driver required by the relay
                           board (optional component).

  Configuration File       relay_mapping.cfg — set your COM port and
                           custom relay labels.


===============================================================================
  SYSTEM REQUIREMENTS
===============================================================================

  - Windows 10 or later (64-bit)
  - One free USB port
  - HW-34 / USB-RELAY04 relay board


===============================================================================
  INSTALLATION STEPS
===============================================================================

  1. Run  USB-RELAY04_Setup_1.0.0.exe

  2. If prompted by Windows SmartScreen, click "More info" then
     "Run anyway". The app is not code-signed, so Windows may warn.

  3. Choose an install location (default: C:\Program Files\USB-RELAY04).

  4. Select components:

       [x] GUI Application        (always installed)
       [x] System Tray Control    (recommended)
       [ ] Command-Line Interface (for scripting)
       [ ] PL2303 USB-Serial Driver

  5. Optional tasks:

       [ ] Create desktop shortcuts
       [ ] Start Tray Control automatically on Windows login

  6. Click Install.

  7. If you selected the PL2303 driver, a message will tell you where
     it was copied. Navigate there and run the driver installer as
     Administrator before plugging in the relay board.

  8. Click Finish. The GUI and/or Tray app will launch automatically
     if you leave those checkboxes selected.


===============================================================================
  FIRST-TIME SETUP
===============================================================================

  1. Install the PL2303 driver if you haven't already
     (see step 7 above).

  2. Plug in the USB-RELAY04 board.

  3. Open Device Manager (Win+X -> Device Manager) and note the
     COM port assigned under "Ports (COM & LPT)".

  4. Edit the configuration file:
       - Open the install folder (default: C:\Program Files\USB-RELAY04)
       - Open  relay_mapping.cfg  with Notepad
       - Change the line:  port = COM3  to match your port
       - Optionally rename the relay labels
       - Save and close

  5. Launch the GUI from the Start Menu or desktop shortcut.
     Select your COM port and click Connect.


===============================================================================
  HOW TO USE
===============================================================================

  GUI Application
  ---------------
    - Launch from Start Menu: USB-RELAY04 > USB-RELAY04 GUI
    - Select COM port from the dropdown
    - Click Connect
    - Use individual relay switches or ALL ON / ALL OFF buttons
    - Toggle Dark/Light theme with the switch in the header
    - Enable "Top" to keep the window always on top

  System Tray
  -----------
    - Launch from Start Menu: USB-RELAY04 > USB-RELAY04 Tray Control
    - A coloured circle icon appears in your notification area:
        Green  = all relays ON
        Red    = all relays OFF
        Amber  = idle (no command sent yet)
    - LEFT-CLICK the icon to toggle all relays ON <-> OFF
    - RIGHT-CLICK for a menu: ALL ON, ALL OFF, Port info, Exit
    - Hover over the icon to see a status tooltip

    Tip: If you enabled "Start on login" during install, the tray
    icon will appear automatically every time you log in.

    Tip: If the icon is hidden, click the "^" arrow in the
    notification area. To pin it permanently:
    Settings > Personalization > Taskbar > Other system tray icons

  Command-Line Interface
  ----------------------
    Open a terminal (cmd or PowerShell) and navigate to the install
    folder, then run:

      usb_relay_hw34_cli.exe --init --on 1 2      Turn on relays 1 and 2
      usb_relay_hw34_cli.exe --init --off 3 4      Turn off relays 3 and 4
      usb_relay_hw34_cli.exe --init --on 1 2 3 4   All on

    Note: The CLI has the COM port hardcoded at the top of its source.
    The installed .exe uses COM10 by default. If you need a different
    port for CLI usage, use the GUI or Tray app instead.


===============================================================================
  CONFIGURATION FILE  (relay_mapping.cfg)
===============================================================================

  Located in the install folder. Edit with any text editor.

    [SerialPort]
    port = COM3                     <-- Your relay's COM port

    [Relays]
    relay1label = PSU 1 Control     <-- Custom label for Relay 1
    relay2label = PSU 2 Control     <-- Custom label for Relay 2
    relay3label = Motor Control     <-- Custom label for Relay 3
    relay4label = CAN Short to GND  <-- Custom label for Relay 4

    [UI]
    theme = Dark                    <-- Light | Dark | System
    auto_refresh_ports = 1          <-- Auto-detect COM ports (1=on, 0=off)
    ports_refresh_ms = 3000         <-- Port scan interval in milliseconds

  The GUI saves changes to this file automatically (last-used port,
  theme preference). Your relay labels are preserved across updates.


===============================================================================
  UNINSTALLING
===============================================================================

  - Start Menu: USB-RELAY04 > Uninstall USB-RELAY04
  - Or: Settings > Apps > USB-RELAY04 Control Suite > Uninstall

  The uninstaller will:
    - Stop the tray app if running
    - Remove all installed files
    - Remove Start Menu and desktop shortcuts
    - Remove the auto-start registry entry (if set)
    - Preserve relay_mapping.cfg (your config is never deleted)


===============================================================================
  TROUBLESHOOTING
===============================================================================

  "Windows protected your PC" (SmartScreen)
    The installer is not code-signed. Click "More info" then "Run anyway".

  GUI or Tray won't start (no error)
    Check Windows Event Viewer > Application logs for details.
    Make sure no antivirus is blocking the .exe files.

  "could not open port 'COMx'"
    Wrong COM port. Check Device Manager and update relay_mapping.cfg.

  Relay does not respond
    1. Verify the PL2303 driver is installed (Device Manager > Ports).
    2. Try a different USB port or cable.
    3. Disconnect and reconnect in the GUI.

  Tray icon not visible
    Click the "^" arrow in the notification area to show hidden icons.
    To pin: Settings > Personalization > Taskbar > Other system tray icons.


===============================================================================
  FILES INSTALLED
===============================================================================

  usb_relay_hw34_gui.exe     GUI application (standalone, no Python needed)
  relay_tray.exe             System tray quick-control (standalone)
  usb_relay_hw34_cli.exe     Command-line interface (standalone)
  relay_mapping.cfg          Configuration file
  README.txt                 Full project documentation
  INSTALLER_README.txt       This file
  Driver\                    PL2303 USB-to-Serial driver


===============================================================================
  PROJECT
===============================================================================

  GitHub:  https://github.com/appo02/HW-34-USB-RELAY04-UI-and-Tray-Icon
  Board:   HW-34 / USB-RELAY04 (seeit.fr)

===============================================================================
