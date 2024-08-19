import time
import serial
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import sys
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
        raise ValueError(f"Unexpected response from relay: {response.hex() if response else 'None'}")

def control_relay(ser, byte_command):
    ser.write(byte_command)
    print(f"Command {byte_command.hex()} sent to relay")
    print(10*"-")

def update_relay_state(ser, relay_state, bit_position, turn_on):
    if turn_on:
        relay_state &= ~(1 << bit_position)
    else:
        relay_state |= (1 << bit_position)
    print(f"Relay state: {relay_state:08b}")
    control_relay(ser, bytes([relay_state]))
    return relay_state

class RelayControlApp:
    def __init__(self, root, relay_labels, ser):
        self.root = root
        self.root.title("USB-RELAY04 Control")
        self.relay_state = 0xFF  # All relays off initially
        self.ser = ser

        self.buttons = []
        for i in range(4):
            button = tk.Button(root, text=f"Relay {i+1} OFF", command=lambda i=i: self.toggle_relay(i))
            button.grid(row=0, column=i, padx=10, pady=10)
            self.buttons.append(button)
            
            label = tk.Label(root, text=relay_labels[i])
            label.grid(row=1, column=i, padx=10, pady=10)

        self.log_text = ScrolledText(root, wrap=tk.WORD, width=50, height=5)
        self.log_text.grid(row=2, column=0, columnspan=4, padx=10, pady=10)
        self.log_text.config(state=tk.DISABLED)

        # Redirect stdout to the text box
        sys.stdout = TextRedirector(self.log_text, "stdout")

        # Add "Always on Top" button
        self.always_on_top_button = tk.Button(root, text="Always on Top: OFF", command=self.toggle_always_on_top)
        self.always_on_top_button.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

    def toggle_relay(self, relay):
        print(f"Relay {relay+1} toggled")
        current_state = (self.relay_state & (1 << relay)) == 0
        self.relay_state = update_relay_state(self.ser, self.relay_state, relay, not current_state)
        self.update_button_text(relay, not current_state)

    def update_button_text(self, relay, state):
        self.buttons[relay].config(text=f"Relay {relay+1} {'ON' if state else 'OFF'}")

    def toggle_always_on_top(self):
        current_state = self.root.attributes('-topmost')
        new_state = not current_state
        self.root.attributes('-topmost', new_state)
        self.always_on_top_button.config(text=f"Always on Top: {'ON' if new_state else 'OFF'}")

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

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    serial_port = config.get('SerialPort', 'port', fallback='COM10')
    relay_labels = [
        config.get('Relays', 'Relay1Label', fallback='Relay 1 Control'),
        config.get('Relays', 'Relay2Label', fallback='Relay 2 Control'),
        config.get('Relays', 'Relay3Label', fallback='Relay 3 Control'),
        config.get('Relays', 'Relay4Label', fallback='Relay 4 Control')
    ]
    return serial_port, relay_labels

def main():
    serial_port, relay_labels = read_config('relay_mapping.cfg')
    
    try:
        ser = serial.Serial(serial_port, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=5)
        print("Initializing relay...")
        # initialize_relay(ser)        
    except Exception as e:
        messagebox.showerror("Initialization Error", str(e))
        return

    root = tk.Tk()
    app = RelayControlApp(root, relay_labels, ser)
    root.mainloop()

    ser.close()

if __name__ == "__main__":
    main()