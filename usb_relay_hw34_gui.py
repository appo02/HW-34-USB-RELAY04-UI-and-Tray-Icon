import time
import serial
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import sys
import os
import configparser

def initialize_relay(ser):
    ser.write(b'\x50')
    time.sleep(1)
    response = ser.read(1)
    ser.write(b'\x51')
    print(50*"-")
    print(f"Received response: {response.hex() if response else 'None'}")
    print(50*"-")
    if response in [b'\xAD', b'\xAB', b'\xAC']:
        print(f"Relay initialized with response: {response.hex()}")
    else:
        print(f"Unexpected response from relay: {response.hex() if response else 'None'}")

def control_relay(ser, byte_command):
    ser.write(byte_command)
    print(f"Command {byte_command.hex()} sent to relay")

def update_relay_state(ser, relay_state, bit_position, turn_on):
    if turn_on:
        relay_state &= ~(1 << bit_position)
    else:
        relay_state |= (1 << bit_position)
    print(f"Relay state: {~relay_state & 0x0F:04b}")
    control_relay(ser, bytes([relay_state]))
    return relay_state

class RelayControlApp:
    def __init__(self, root, relay_labels, config):
        self.root = root
        self.root.title("USB-RELAY04 Control")
        self.relay_state = 0xF  # All relays off initially
        self.ser = None
        self.config = config

        self.serial_port_entry = tk.Entry(root)
        self.serial_port_entry.grid(row=0, column=0, padx=5, pady=5)
        self.serial_port_entry.insert(0, config['SerialPort']['port'])

        self.connect_button = tk.Button(root, text="Connect", command=self.toggle_serial_connection)
        self.connect_button.grid(row=0, column=1, padx=5, pady=5)

        self.buttons = []
        for i in range(4):
            button = tk.Button(root, text=f"Relay {i+1} OFF", state=tk.DISABLED, command=lambda i=i: self.toggle_relay(i))
            button.grid(row=1, column=i, padx=5, pady=5)
            self.buttons.append(button)
            
            label = tk.Label(root, text=relay_labels[i])
            label.grid(row=2, column=i, padx=5, pady=5)

        self.log_text = ScrolledText(root, wrap=tk.WORD, width=50, height=5)
        self.log_text.grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)

        # Redirect stdout to the text box
        sys.stdout = TextRedirector(self.log_text, "stdout")

        # Add "Always on Top" button
        self.always_on_top_button = tk.Button(root, text="Always on Top: OFF", command=self.toggle_always_on_top)
        self.always_on_top_button.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

        # Initially disable key bindings
        self.update_key_bindings(enable=False)

    def toggle_serial_connection(self):
        if self.ser and self.ser.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        serial_port = self.serial_port_entry.get()
        try:
            self.ser = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=5)
            print("Initializing relay...")
            initialize_relay(self.ser)
            for button in self.buttons:
                button.config(state=tk.NORMAL)
            self.save_serial_port(serial_port)
            self.connect_button.config(text="Disconnect")
            self.update_key_bindings(enable=True)
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def disconnect_serial(self):
        if self.ser:
            self.ser.close()
            self.ser = None
            for button in self.buttons:
                button.config(state=tk.DISABLED)
            self.connect_button.config(text="Connect")
            self.update_key_bindings(enable=False)
            print("Serial port disconnected")

    def toggle_relay(self, relay):
        print(f"Relay {relay+1} toggled")
        current_state = (self.relay_state & (1 << relay)) == 0
        self.relay_state = update_relay_state(self.ser, self.relay_state, relay, not current_state)
        print(f"Relay {relay+1} {'ON' if not current_state else 'OFF'}")
        self.update_button_text(relay, not current_state)

    def update_button_text(self, relay, state):
        self.buttons[relay].config(text=f"Relay {relay+1} {'ON' if state else 'OFF'}")

    def toggle_always_on_top(self):
        current_state = self.root.attributes('-topmost')
        new_state = not current_state
        self.root.attributes('-topmost', new_state)
        self.always_on_top_button.config(text=f"Always on Top: {'ON' if new_state else 'OFF'}")

    def save_serial_port(self, port):
        self.config['SerialPort']['port'] = port
        with open('relay_mapping.cfg', 'w') as configfile:
            self.config.write(configfile)

    def update_key_bindings(self, enable):
        if enable:
            self.root.bind('1', lambda event: self.toggle_relay(0))
            self.root.bind('2', lambda event: self.toggle_relay(1))
            self.root.bind('3', lambda event: self.toggle_relay(2))
            self.root.bind('4', lambda event: self.toggle_relay(3))
        else:
            self.root.unbind('1')
            self.root.unbind('2')
            self.root.unbind('3')
            self.root.unbind('4')

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, str)
        self.widget.config(state=tk.DISABLED)
        self.widget.see(tk.END)

    def flush(self):
        pass

def main():
    config = configparser.ConfigParser()
    config.read('relay_mapping.cfg')

    if 'SerialPort' not in config:
        config['SerialPort'] = {'port': 'COM5'}

    if 'Relays' not in config:
        config['Relays'] = {
            'Relay1Label': 'PSU 1 Control',
            'Relay2Label': 'PSU 2 Control',
            'Relay3Label': 'Motor Control',
            'Relay4Label': 'CAN Short to Ground'
        }

    relay_labels = [
        config['Relays']['Relay1Label'],
        config['Relays']['Relay2Label'],
        config['Relays']['Relay3Label'],
        config['Relays']['Relay4Label']
    ]

    root = tk.Tk()
    app = RelayControlApp(root, relay_labels, config)
    root.mainloop()

    if app.ser:
        app.ser.close()

if __name__ == "__main__":
    main()