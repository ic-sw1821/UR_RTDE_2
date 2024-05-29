# Original ChatGPT Python code for Arduino

import serial.tools.list_ports
import time

# Function to find the Arduino port
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "ACM" in str(port):
            return port.device
    return None

# Function to control the solenoid valves
def valve(command):
    start = time.time()
    print()
    print(start)
    serialInst.write(bytes(command, "utf-8"))
    time.sleep(0.1)  # Small delay to ensure command is sent
    if serialInst.in_waiting > 0:
        response = serialInst.readline().decode("utf-8").strip()
        print(response)
    if command == "exit":
        serialInst.close()
        print("Program ended")
    end = time.time()
    print(end)
    print(end - start)

# Find and connect to the Arduino
arduino_port = find_arduino_port()
if arduino_port is None:
    print("Arduino not found")
else:
    print(f"Connecting to Arduino on port {arduino_port}")
    serialInst = serial.Serial(port=arduino_port, baudrate=9600, timeout=1)
    time.sleep(2)  # Wait for the connection to establish
    # Example usage`
    valve("1")
    time.sleep(2)
    valve("3")
    time.sleep(2)
    valve("4")
    time.sleep(2)
    valve("exit")




