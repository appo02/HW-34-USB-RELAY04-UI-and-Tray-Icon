
import time
import sys
import configparser

import serial
from serial.tools import list_ports

import customtkinter as ctk
from tkinter import messagebox

from PIL import Image, ImageDraw


# =========================================================
# Config helpers
# =========================================================
CFG_PATH = "relay_mapping.cfg"


def load_config_file(path=CFG_PATH):
    config = configparser.ConfigParser()
    config.read(path)

    if "SerialPort" not in config:
        config["SerialPort"] = {"port": "COM5"}

    if "Relays" not in config:
        config["Relays"] = {
            "Relay1Label": "PSU 1 Control",
            "Relay2Label": "PSU 2 Control",
            "Relay3Label": "Motor Control",
            "Relay4Label": "CAN Short to Ground",
        }

    if "UI" not in config:
        config["UI"] = {}

    # Defaults
    config["UI"].setdefault("theme", "Light")              # Light | Dark | System
    config["UI"].setdefault("auto_refresh_ports", "1")     # 1/0
    config["UI"].setdefault("ports_refresh_ms", "3000")    # ms

    return config


def save_config_file(config, path=CFG_PATH):
    with open(path, "w") as f:
        config.write(f)


# =========================================================
# Relay low-level functions
# =========================================================
def initialize_relay(ser):
    ser.write(b"\x50")
    time.sleep(1)
    response = ser.read(1)
    ser.write(b"\x51")
    return response


def control_relay(ser, byte_command):
    ser.write(byte_command)


def update_relay_state(ser, relay_state, bit_position, turn_on):
    """
    Board logic:
      - bit = 0 -> relay ON
      - bit = 1 -> relay OFF
    """
    if turn_on:
        relay_state &= ~(1 << bit_position)     # ON  => clear bit
    else:
        relay_state |= (1 << bit_position)      # OFF => set bit ✅ fixed

    control_relay(ser, bytes([relay_state & 0xFF]))
    return relay_state


# =========================================================
# Minimal icon generator (no external files)
# =========================================================
def make_icon(kind: str, size: int = 22, fg="#111111", bg=(0, 0, 0, 0)):
    """
    Draw simple icons using PIL so you don't need image files.
    kinds: plug, unplug, refresh, power, sun, moon
    """
    img = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(img)

    def line(xy, w=2):
        d.line(xy, fill=fg, width=w)

    def rect(xy, w=2):
        d.rectangle(xy, outline=fg, width=w)

    def ellipse(xy, w=2, fill=None):
        d.ellipse(xy, outline=fg, width=w, fill=fill)

    if kind == "plug":
        rect((6, 8, 16, 16), w=2)
        line([(8, 6), (8, 8)], w=2)
        line([(14, 6), (14, 8)], w=2)
        line([(11, 16), (11, 20)], w=2)

    elif kind == "unplug":
        rect((6, 8, 16, 16), w=2)
        line([(8, 6), (8, 8)], w=2)
        line([(14, 6), (14, 8)], w=2)
        line([(11, 16), (11, 20)], w=2)
        line([(5, 18), (18, 5)], w=2)

    elif kind == "refresh":
        ellipse((5, 5, 17, 17), w=2)
        line([(12, 4), (17, 4), (17, 9)], w=2)
        line([(17, 4), (19, 6)], w=2)

    elif kind == "power":
        ellipse((5, 5, 17, 17), w=2)
        line([(11, 3), (11, 10)], w=2)

    elif kind == "sun":
        ellipse((7, 7, 15, 15), w=2)
        for (x1, y1, x2, y2) in [
            (11, 1, 11, 5), (11, 17, 11, 21),
            (1, 11, 5, 11), (17, 11, 21, 11),
            (4, 4, 6, 6), (16, 16, 18, 18),
            (16, 6, 18, 4), (4, 18, 6, 16),
        ]:
            line([(x1, y1), (x2, y2)], w=2)

    elif kind == "moon":
        ellipse((6, 5, 18, 17), w=2)
        d.ellipse((9, 5, 21, 17), fill=bg)

    else:
        ellipse((9, 9, 13, 13), w=2, fill=fg)

    return img


# =========================================================
# Log redirector (print -> textbox)
# =========================================================
class TextRedirector:
    def __init__(self, app):
        self.app = app

    def write(self, s):
        if s:
            self.app.append_log(s)

    def flush(self):
        pass


# =========================================================
# Main App (CustomTkinter)
# =========================================================
class RelayControlApp(ctk.CTk):
    GREEN = "#2ecc71"
    RED = "#e74c3c"
    TEXT_ON = "#ffffff"

    CONNECT_GREEN = "#27ae60"
    CONNECT_RED = "#c0392b"

    CARD_BG = ("#f6f6f6", "#1f1f1f")
    CARD_BORDER = ("#dddddd", "#2a2a2a")
    RELAY_CARD_BG = ("#ffffff", "#151515")

    def __init__(self, config):
        super().__init__()
        self.cfg = config

        # Relay state (low nibble)
        self.ser = None
        self.relay_state = 0x0F  # all OFF initially

        # Ports mapping (device -> description)
        self.ports_map = {}

        # Window base (we will auto-size to content after build)
        self.title("USB-RELAY04 Control (Modern)")
        self.geometry("760x520")
        self.minsize(680, 480)

        # Redirect stdout to GUI
        self._original_stdout = sys.stdout
        sys.stdout = TextRedirector(self)

        # Theme-aware icons
        self.icons = {}
        self.build_icons()

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # log expands

        # Build UI
        self.build_header()
        self.build_relays_2x2()
        self.build_log()

        # Initial state
        self.set_connected(False)
        self.refresh_visuals()

        # Populate ports + auto refresh
        self.refresh_ports(initial=True)

        self.auto_refresh_enabled = self.cfg["UI"].get("auto_refresh_ports", "1") == "1"
        self.ports_refresh_ms = int(self.cfg["UI"].get("ports_refresh_ms", "3000"))
        self._ports_job = None
        if self.auto_refresh_enabled:
            self.schedule_ports_refresh()

        # Size to required content so nothing is clipped
        self.after(50, self.size_to_content_and_center)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.log("Ready. Select COM port and press Connect.\n")

    # -----------------------------
    # Window sizing: ensure no clipping
    # -----------------------------
    def size_to_content_and_center(self, max_w_margin=80, max_h_margin=100):
        """
        Makes window big enough to fit all widgets (requested size),
        but not larger than screen. Then centers it.
        This guarantees no cropped buttons at startup.
        """
        try:
            self.update_idletasks()
            req_w = self.winfo_reqwidth()
            req_h = self.winfo_reqheight()

            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()

            w = min(req_w + 20, sw - max_w_margin)
            h = min(req_h + 20, sh - max_h_margin)

            # Ensure not below minimum
            min_w, min_h = self.minsize()
            w = max(w, min_w)
            h = max(h, min_h)

            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)

            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    # -----------------------------
    # Icons
    # -----------------------------
    def theme_fg(self):
        return "#FFFFFF" if ctk.get_appearance_mode().lower() == "dark" else "#111111"

    def build_icons(self):
        fg = self.theme_fg()
        bg = (0, 0, 0, 0)

        def ctk_img(pil_img):
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(22, 22))

        self.icons["plug"] = ctk_img(make_icon("plug", fg=fg, bg=bg))
        self.icons["unplug"] = ctk_img(make_icon("unplug", fg=fg, bg=bg))
        self.icons["refresh"] = ctk_img(make_icon("refresh", fg=fg, bg=bg))
        self.icons["power"] = ctk_img(make_icon("power", fg=fg, bg=bg))
        self.icons["sun"] = ctk_img(make_icon("sun", fg=fg, bg=bg))
        self.icons["moon"] = ctk_img(make_icon("moon", fg=fg, bg=bg))

    def refresh_icon_bindings(self):
        connected = self.ser is not None and self.ser.is_open
        self.connect_btn.configure(image=self.icons["unplug"] if connected else self.icons["plug"])
        self.refresh_ports_btn.configure(image=self.icons["refresh"])
        self.all_on_btn.configure(image=self.icons["power"])
        self.all_off_btn.configure(image=self.icons["power"])
        self.theme_icon.configure(image=self.icons["moon"] if self.theme_switch.get() else self.icons["sun"])

    # -----------------------------
    # Header
    # -----------------------------
    def build_header(self):
        header = ctk.CTkFrame(
            self, corner_radius=14,
            fg_color=self.CARD_BG, border_width=1, border_color=self.CARD_BORDER
        )
        header.grid(row=0, column=0, padx=12, pady=(12, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        # Left: title
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, rowspan=2, sticky="w", padx=12, pady=10)

        ctk.CTkLabel(left, text="USB Relay Controller", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(left, text="HW-34 / USB-RELAY04 • Modern UI", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, sticky="w", pady=(2, 0)
        )

        # Right: controls in a compact 2-row grid (no overflow)
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=10)

        # Row 0: Port + Refresh + Connect
        self.port_var = ctk.StringVar(value="(no ports)")
        self.port_menu = ctk.CTkOptionMenu(right, variable=self.port_var, values=["(no ports)"], width=140)
        self.port_menu.grid(row=0, column=0, padx=(0, 8), pady=(0, 6), sticky="e")

        self.refresh_ports_btn = ctk.CTkButton(right, text="", width=38, image=self.icons["refresh"],
                                               command=lambda: self.refresh_ports(initial=False))
        self.refresh_ports_btn.grid(row=0, column=1, padx=(0, 8), pady=(0, 6))

        self.connect_btn = ctk.CTkButton(right, text="Connect", width=130, image=self.icons["plug"],
                                         compound="left", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=2, pady=(0, 6))

        # Row 1: Status + Always on top + Theme
        self.status_badge = ctk.CTkLabel(
            right, text="DISCONNECTED",
            text_color=self.TEXT_ON, fg_color=self.CONNECT_RED,
            corner_radius=10, padx=10, pady=4,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.status_badge.grid(row=1, column=0, padx=(0, 8), sticky="e")

        self.top_switch = ctk.CTkSwitch(right, text="Top", command=self.toggle_always_on_top)
        self.top_switch.grid(row=1, column=1, padx=(0, 8), sticky="e")

        self.theme_switch = ctk.CTkSwitch(right, text="Dark", command=self.toggle_theme)
        self.theme_switch.grid(row=1, column=2, sticky="e")

        self.theme_icon = ctk.CTkLabel(right, text="", image=self.icons["sun"])
        self.theme_icon.grid(row=1, column=3, padx=(8, 0), sticky="e")

        # Port description line (under header, short and wraps)
        self.port_desc = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w"
        )
        self.port_desc.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="ew")

        # Apply persisted theme
        current = ctk.get_appearance_mode().lower()
        if current == "dark":
            self.theme_switch.select()
            self.theme_icon.configure(image=self.icons["moon"])
        else:
            self.theme_switch.deselect()
            self.theme_icon.configure(image=self.icons["sun"])

    # -----------------------------
    # Relay panel: 2x2 grid (guarantees fit)
    # -----------------------------
    def build_relays_2x2(self):
        panel = ctk.CTkFrame(
            self, corner_radius=14,
            fg_color=self.CARD_BG, border_width=1, border_color=self.CARD_BORDER
        )
        panel.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)

        # Top bar: title + ALL buttons (compact)
        bar = ctk.CTkFrame(panel, fg_color="transparent")
        bar.grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="ew")
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(bar, text="Relay Controls", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w"
        )

        btns = ctk.CTkFrame(bar, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e")

        self.all_on_btn = ctk.CTkButton(
            btns, text="ALL ON", width=110, height=32,
            fg_color=self.GREEN, hover_color="#28b463",
            text_color=self.TEXT_ON,
            image=self.icons["power"], compound="left",
            command=self.turn_all_on
        )
        self.all_on_btn.grid(row=0, column=0, padx=(0, 8))

        self.all_off_btn = ctk.CTkButton(
            btns, text="ALL OFF", width=110, height=32,
            fg_color=self.RED, hover_color="#cb4335",
            text_color=self.TEXT_ON,
            image=self.icons["power"], compound="left",
            command=self.turn_all_off
        )
        self.all_off_btn.grid(row=0, column=1)

        # Relay cards 2x2
        self.relay_switches = []
        self.relay_pills = []

        relay_names = [
            self.cfg["Relays"]["Relay1Label"],
            self.cfg["Relays"]["Relay2Label"],
            self.cfg["Relays"]["Relay3Label"],
            self.cfg["Relays"]["Relay4Label"],
        ]

        positions = [(1, 0), (1, 1), (2, 0), (2, 1)]  # 2 rows, 2 cols

        for i in range(4):
            r, c = positions[i]
            card = ctk.CTkFrame(
                panel, corner_radius=14,
                fg_color=self.RELAY_CARD_BG,
                border_width=1, border_color=self.CARD_BORDER
            )
            card.grid(row=r, column=c, padx=12 if c == 0 else 8, pady=(0, 12), sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=f"Relay {i+1}", font=ctk.CTkFont(size=13, weight="bold")).grid(
                row=0, column=0, padx=12, pady=(10, 2), sticky="w"
            )
            ctk.CTkLabel(card, text=relay_names[i], font=ctk.CTkFont(size=11)).grid(
                row=1, column=0, padx=12, pady=(0, 8), sticky="w"
            )

            pill = ctk.CTkLabel(
                card, text="OFF",
                text_color=self.TEXT_ON,
                fg_color=self.RED,
                corner_radius=10,
                padx=10, pady=3,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            pill.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="w")
            self.relay_pills.append(pill)

            sw = ctk.CTkSwitch(card, text="", command=lambda idx=i: self.on_relay_switch(idx))
            sw.grid(row=3, column=0, padx=12, pady=(0, 10), sticky="w")
            self.relay_switches.append(sw)

    # -----------------------------
    # Log
    # -----------------------------
    def build_log(self):
        log_frame = ctk.CTkFrame(
            self, corner_radius=14,
            fg_color=self.CARD_BG, border_width=1, border_color=self.CARD_BORDER
        )
        log_frame.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="Log", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(10, 6), sticky="w"
        )

        self.log_box = ctk.CTkTextbox(log_frame, wrap="word", height=140)
        self.log_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.log_box.configure(state="disabled")

    # -----------------------------
    # Logging
    # -----------------------------
    def append_log(self, text):
        def _append():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", text)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, _append)

    def log(self, msg):
        print(msg, end="" if msg.endswith("\n") else "\n")

    # -----------------------------
    # Ports (show COMx only, description in separate label)
    # -----------------------------
    def enumerate_ports(self):
        mapping = {}
        for p in list_ports.comports():
            vidpid = ""
            if getattr(p, "vid", None) is not None and getattr(p, "pid", None) is not None:
                vidpid = f" (VID:PID={p.vid:04X}:{p.pid:04X})"
            desc = f"{p.description}{vidpid}"
            mapping[p.device] = desc
        return mapping

    def refresh_ports(self, initial=False):
        self.ports_map = self.enumerate_ports()
        devices = sorted(self.ports_map.keys())

        if not devices:
            devices = ["(no ports)"]
            self.port_menu.configure(values=devices)
            self.port_var.set(devices[0])
            self.port_desc.configure(text="")
            return

        self.port_menu.configure(values=devices)

        # Keep current selection if possible, else restore saved port
        cur = self.port_var.get()
        saved = self.cfg["SerialPort"].get("port", "")

        if cur in devices:
            self.port_var.set(cur)
        elif saved in devices:
            self.port_var.set(saved)
        else:
            self.port_var.set(devices[0])

        self.update_port_desc()

        if not initial:
            self.log("Ports refreshed.\n")

    def update_port_desc(self):
        dev = self.port_var.get()
        desc = self.ports_map.get(dev, "")
        self.port_desc.configure(text=(f"{dev}: {desc}" if desc else ""))

    def schedule_ports_refresh(self):
        if self._ports_job:
            try:
                self.after_cancel(self._ports_job)
            except Exception:
                pass
        self._ports_job = self.after(self.ports_refresh_ms, self._auto_refresh_ports)

    def _auto_refresh_ports(self):
        try:
            self.refresh_ports(initial=True)
        except Exception:
            pass
        if self.auto_refresh_enabled:
            self.schedule_ports_refresh()

    # -----------------------------
    # Theme
    # -----------------------------
    def toggle_theme(self):
        is_dark = bool(self.theme_switch.get())
        mode = "Dark" if is_dark else "Light"
        ctk.set_appearance_mode(mode)

        self.build_icons()
        self.refresh_icon_bindings()
        self.cfg["UI"]["theme"] = mode
        save_config_file(self.cfg)

    # -----------------------------
    # Connection / UI state
    # -----------------------------
    def set_connected(self, connected: bool):
        if connected:
            self.connect_btn.configure(
                text="Disconnect",
                fg_color=self.CONNECT_GREEN,
                hover_color="#1e8449",
                image=self.icons["unplug"],
                compound="left"
            )
            self.status_badge.configure(text="CONNECTED", fg_color=self.CONNECT_GREEN)
        else:
            self.connect_btn.configure(
                text="Connect",
                fg_color=self.CONNECT_RED,
                hover_color="#922b21",
                image=self.icons["plug"],
                compound="left"
            )
            self.status_badge.configure(text="DISCONNECTED", fg_color=self.CONNECT_RED)

        state = "normal" if connected else "disabled"
        for sw in self.relay_switches:
            sw.configure(state=state)

        self.all_on_btn.configure(state=state)
        self.all_off_btn.configure(state=state)

        self.refresh_icon_bindings()

    def low_nibble(self):
        return self.relay_state & 0x0F

    def all_on(self):
        return self.low_nibble() == 0x00

    def all_off(self):
        return self.low_nibble() == 0x0F

    def refresh_all_buttons_enabled_state(self):
        if not (self.ser and self.ser.is_open):
            self.all_on_btn.configure(state="disabled")
            self.all_off_btn.configure(state="disabled")
            return
        self.all_on_btn.configure(state="disabled" if self.all_on() else "normal")
        self.all_off_btn.configure(state="disabled" if self.all_off() else "normal")

    def refresh_visuals(self):
        for i in range(4):
            is_on = (self.relay_state & (1 << i)) == 0
            if is_on:
                self.relay_switches[i].select()
            else:
                self.relay_switches[i].deselect()

            self.relay_pills[i].configure(text="ON" if is_on else "OFF",
                                          fg_color=self.GREEN if is_on else self.RED)

        if self.ser and self.ser.is_open:
            self.refresh_all_buttons_enabled_state()

        self.refresh_icon_bindings()

    # -----------------------------
    # Actions
    # -----------------------------
    def toggle_always_on_top(self):
        self.attributes("-topmost", bool(self.top_switch.get()))

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        dev = self.port_var.get()
        if not dev or dev == "(no ports)":
            messagebox.showerror("Connection Error", "No serial ports found.")
            return

        # Update desc line immediately
        self.update_port_desc()

        try:
            self.ser = serial.Serial(
                dev,
                9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=5,
            )

            self.log("Initializing relay...\n")
            resp = initialize_relay(self.ser)
            self.log(f"Received response: {resp.hex() if resp else 'None'}\n")

            # Sync device to current internal state (starts ALL OFF)
            control_relay(self.ser, bytes([self.relay_state & 0xFF]))

            # Save selected port
            self.cfg["SerialPort"]["port"] = dev
            save_config_file(self.cfg)

            self.set_connected(True)
            self.refresh_visuals()
            self.log(f"Connected on {dev}. Initial state: ALL OFF\n")

        except Exception as e:
            self.ser = None
            self.set_connected(False)
            messagebox.showerror("Connection Error", str(e))

    def disconnect_serial(self):
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        self.ser = None
        self.set_connected(False)
        self.log("Disconnected.\n")

    def on_relay_switch(self, relay_index: int):
        if not (self.ser and self.ser.is_open):
            self.refresh_visuals()
            return

        desired_on = bool(self.relay_switches[relay_index].get())
        current_on = (self.relay_state & (1 << relay_index)) == 0
        if desired_on == current_on:
            return

        self.log(f"Relay {relay_index + 1} -> {'ON' if desired_on else 'OFF'}\n")
        self.relay_state = update_relay_state(self.ser, self.relay_state, relay_index, turn_on=desired_on)
        self.refresh_visuals()

    def set_all_relays(self, turn_on: bool):
        if not (self.ser and self.ser.is_open):
            return

        if turn_on:
            self.relay_state = (self.relay_state & 0xF0) | 0x00
        else:
            self.relay_state = (self.relay_state & 0xF0) | 0x0F

        control_relay(self.ser, bytes([self.relay_state & 0xFF]))
        self.refresh_visuals()
        self.log("All relays " + ("ON\n" if turn_on else "OFF\n"))

    def turn_all_on(self):
        self.set_all_relays(True)

    def turn_all_off(self):
        self.set_all_relays(False)

    # -----------------------------
    # Close
    # -----------------------------
    def on_close(self):
        if self._ports_job:
            try:
                self.after_cancel(self._ports_job)
            except Exception:
                pass

        try:
            sys.stdout = self._original_stdout
        except Exception:
            pass

        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

        self.destroy()


# =========================================================
# Main
# =========================================================
def main():
    cfg = load_config_file()

    theme = cfg["UI"].get("theme", "Light").capitalize()
    if theme not in ("Light", "Dark", "System"):
        theme = "Light"

    ctk.set_appearance_mode(theme)
    ctk.set_default_color_theme("blue")

    app = RelayControlApp(cfg)

    # Update icon bindings after build
    app.refresh_icon_bindings()

    # Update port desc when user changes selection
    # (CTkOptionMenu doesn't expose a direct "changed" event reliably,
    #  so we poll lightly without affecting performance.)
    def poll_port_desc():
        app.update_port_desc()
        app.after(600, poll_port_desc)
    app.after(600, poll_port_desc)

    app.mainloop()


if __name__ == "__main__":
    main()
