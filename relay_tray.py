"""
System-tray quick-control for USB-RELAY04 (HW-34).

Provides two always-available actions in the Windows notification area:
  • ALL ON   – turns all four relay ports on
  • ALL OFF  – turns all four relay ports off

The tray icon colour reflects the current state:
  green = all relays ON, red = all relays OFF, amber = mixed / unknown.

Reads the COM port from relay_mapping.cfg (same file the GUI uses).
"""

import os
import sys
import time
import configparser
import threading

import serial
from PIL import Image, ImageDraw

import pystray

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CFG_PATH = os.path.join(SCRIPT_DIR, "relay_mapping.cfg")

ICON_SIZE = 64
COLOR_ON = "#2ecc71"
COLOR_OFF = "#e74c3c"
COLOR_IDLE = "#f39c12"


def load_port_from_config():
    config = configparser.ConfigParser()
    config.read(CFG_PATH)
    return config.get("SerialPort", "port", fallback="COM3")


# ─────────────────────────────────────────────
# Icon drawing
# ─────────────────────────────────────────────
def _draw_icon(color, label="R"):
    """Create a simple coloured circle icon with a letter."""
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    margin = 4
    d.ellipse(
        [margin, margin, ICON_SIZE - margin, ICON_SIZE - margin],
        fill=color,
    )
    bbox = d.textbbox((0, 0), label)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (ICON_SIZE - tw) // 2
    ty = (ICON_SIZE - th) // 2
    d.text((tx, ty), label, fill="white")
    return img


# ─────────────────────────────────────────────
# Relay helpers (low-level, same protocol as GUI)
# ─────────────────────────────────────────────
class RelayController:
    """Thin wrapper around serial relay commands.

    Keeps the serial port open so commands are near-instant
    (no reconnect + 1 s handshake on every click).
    """

    def __init__(self, port, baudrate=9600, timeout=5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.relay_state = 0x0F  # all OFF
        self._lock = threading.Lock()
        self._ser = None

    # -- serial lifecycle ---
    def _ensure_connected(self):
        """Open + handshake once, then keep the connection alive."""
        if self._ser is not None and self._ser.is_open:
            return
        self._ser = serial.Serial(
            self.port,
            self.baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=self.timeout,
        )
        self._ser.write(b"\x50")
        time.sleep(1)
        self._ser.read(1)
        self._ser.write(b"\x51")

    def close(self):
        with self._lock:
            if self._ser and self._ser.is_open:
                try:
                    self._ser.close()
                except Exception:
                    pass
            self._ser = None

    # -- public API ---
    def all_on(self):
        with self._lock:
            self.relay_state = (self.relay_state & 0xF0) | 0x00
            self._send_state()

    def all_off(self):
        with self._lock:
            self.relay_state = (self.relay_state & 0xF0) | 0x0F
            self._send_state()

    def _send_state(self):
        try:
            self._ensure_connected()
            self._ser.write(bytes([self.relay_state & 0xFF]))
        except serial.SerialException as exc:
            print(f"[relay_tray] Serial error: {exc}", file=sys.stderr)
            # Connection lost – reset so next call will reconnect
            self._ser = None

    @property
    def is_all_on(self):
        return (self.relay_state & 0x0F) == 0x00

    @property
    def is_all_off(self):
        return (self.relay_state & 0x0F) == 0x0F


# ─────────────────────────────────────────────
# Tray app
# ─────────────────────────────────────────────
class RelayTray:
    def __init__(self):
        port = load_port_from_config()
        self.ctrl = RelayController(port)
        self.icon = pystray.Icon(
            name="USB-RELAY04",
            icon=_draw_icon(COLOR_IDLE),
            title="USB-RELAY04  (idle)",
            menu=self._build_menu(),
        )

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem(
                "Toggle ON/OFF",
                self._on_toggle,
                default=True,          # left-click triggers this item
                visible=False,         # hidden from right-click menu
            ),
            pystray.MenuItem(
                "⚡  ALL ON",
                self._on_all_on,
            ),
            pystray.MenuItem(
                "⏻  ALL OFF",
                self._on_all_off,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                f"Port: {self.ctrl.port}",
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._on_exit),
        )

    # -- actions --
    def _on_toggle(self, icon, item):
        """Left-click: toggle between ALL ON and ALL OFF."""
        if self.ctrl.is_all_on:
            threading.Thread(target=self._do_all_off, daemon=True).start()
        else:
            threading.Thread(target=self._do_all_on, daemon=True).start()

    def _on_all_on(self, icon, item):
        threading.Thread(target=self._do_all_on, daemon=True).start()

    def _do_all_on(self):
        self.ctrl.all_on()
        self._refresh_icon()

    def _on_all_off(self, icon, item):
        threading.Thread(target=self._do_all_off, daemon=True).start()

    def _do_all_off(self):
        self.ctrl.all_off()
        self._refresh_icon()

    def _on_exit(self, icon, item):
        self.ctrl.close()
        icon.stop()

    # -- visuals --
    def _refresh_icon(self):
        if self.ctrl.is_all_on:
            self.icon.icon = _draw_icon(COLOR_ON)
            self.icon.title = "USB-RELAY04  [ALL ON]"
        elif self.ctrl.is_all_off:
            self.icon.icon = _draw_icon(COLOR_OFF, "R")
            self.icon.title = "USB-RELAY04  [ALL OFF]"
        else:
            self.icon.icon = _draw_icon(COLOR_IDLE)
            self.icon.title = "USB-RELAY04  (mixed)"

    def run(self):
        self.icon.run()


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def main():
    tray = RelayTray()
    tray.run()


if __name__ == "__main__":
    main()
