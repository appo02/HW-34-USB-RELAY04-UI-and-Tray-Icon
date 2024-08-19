import time
import serial
import argparse

# Configure the serial port (COM10)
ser = serial.Serial('COM10', 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=5)

def initialize_relay():
    # Send 0x50 code to initiate communication
    ser.write(b'\x50')
    time.sleep(1)  # Add a slight delay to allow the relay to respond
    response = ser.read(1)  # Read the response from the relay
    ser.write(b'\x51')
    
    # Debugging: Print the response received
    print(50*"-")
    print(f"Received response: {response.hex() if response else 'None'}")
    print(50*"-")
    if response in [b'\xAD', b'\xAB', b'\xAC']:
        print(f"Relay initialized with response: {response.hex()}")
    else:
        raise ValueError(f"Unexpected response from relay: {response.hex() if response else 'None'}")

def control_relay(byte_command):
    # Send the command byte to control relays
    ser.write(byte_command)
    print(f"Command {byte_command.hex()} sent to relay")

def update_relay_state(relay_state, bit_position, turn_on):
    if turn_on:
        relay_state &= ~(1 << bit_position)  # Turn on the relay
    else:
        relay_state |= (1 << bit_position)  # Turn off the relay
    print(f"Relay state: {relay_state:08b}")
    control_relay(bytes([relay_state]))
    return relay_state

def main():
    parser = argparse.ArgumentParser(description="Control USB relay via command line.")
    parser.add_argument('--init', action='store_true', help="Initialize the relay")
    parser.add_argument('--on', type=int, nargs='*', choices=range(1, 5), help="Turn on relay(s) (1-4)")
    parser.add_argument('--off', type=int, nargs='*', choices=range(1, 5), help="Turn off relay(s) (1-4)")
    
    args = parser.parse_args()

    if args.init:
        initialize_relay()
    
    relay_state = 0xFF  # All relays off initially
    
    if args.on:
        for relay in args.on:
            relay_state = update_relay_state(relay_state, relay - 1, True)
    
    if args.off:
        for relay in args.off:
            relay_state = update_relay_state(relay_state, relay - 1, False)

if __name__ == "__main__":
    try:
        main()
    finally:
        ser.close()  # Close the serial connection