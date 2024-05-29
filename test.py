#  # Arduino integration

# import serial.tools.list_ports
# import time

# ports = serial.tools.list_ports.comports()  # opens comports
# portsList = []
# for each in ports:  # reads each port into a list
#     portsList.append(str(each))
#     print(str(each))
# print(portsList)
# for i in range(len(portsList)):  # finds the port the arduino is linked to
#     if "Arduino" in portsList[i]:
#         use = portsList[i].split()[0]
#         print(use)

# serialInst = serial.Serial(baudrate=9600, port=use)
# # serialInst.open()

# # function to control the solenoid valves for the pneumatic strip feeder and the sprayer
# def valve(command):
#     while True:
#         serialInst.write(bytes(command, "utf-8"))
#         string = serialInst.readline().decode("utf-8")
#         if command == "exit":
#             serialInst.close()
#             print("Program ended")
#             quit()
#         break

# valve("1")
# time.sleep(1)
# print(1)
# valve("1")
# time.sleep(1)
# print(2)
# valve("1")
# time.sleep(1)
# print(3)
# valve("1")
# time.sleep(1)
# print(4)
# valve("1")
# time.sleep(1)
# print(5)

import serial.tools.list_ports
import time

# Function to find the Arduino port
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in str(port):
            return port.device
    return None

# Function to control the solenoid valves
def valve(command):
    serialInst.write(bytes(command, "utf-8"))
    time.sleep(0.1)  # Small delay to ensure command is sent
    if serialInst.in_waiting > 0:
        response = serialInst.readline().decode("utf-8").strip()
        print(response)
    if command == "exit":
        serialInst.close()
        print("Program ended")

# Find and connect to the Arduino
arduino_port = find_arduino_port()
if arduino_port is None:
    print("Arduino not found")
else:
    print(f"Connecting to Arduino on port {arduino_port}")
    serialInst = serial.Serial(port=arduino_port, baudrate=9600, timeout=1)
    time.sleep(2)  # Wait for the connection to establish

    # Example usage
    valve("1")
    time.sleep(2)
    valve("3")
    time.sleep(2)
    valve("4")
    time.sleep(2)
    valve("exit")
