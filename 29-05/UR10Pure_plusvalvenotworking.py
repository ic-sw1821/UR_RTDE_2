# Problem: valves were not printing Arduino outputs (similiar to UR10Pure)

# Imports
# imports needed for UR10 connection
import csv
import sys

sys.path.append('')
import logging
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

# imports needed for other purposes
import rtde.csv_writer as csvWriter
import time
import numpy as np
import serial.tools.list_ports

# =======================================================================================================================
# Initializing UR10 Connection
# establish TCP/IP connection with robot (mode 0)
ROBOT_HOST = '192.168.1.10'
ROBOT_PORT = 30004
con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
connection_state = con.connect()
while connection_state != 0:
    time.sleep(0.5)
    connection_state = con.connect()
print("Robot connected. \n")
con.get_controller_version()

# sync I/O settings from .xml with robot
config_filename = 'control_loop_configuration.xml'  # specify xml file for data synchronization
conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe('state')  # 'state' = outputs specified in .xml
setp_names, setp_types = conf.get_recipe('setp')  # 'setp' = inputs specified in .xml
watchdog_names, watchdog_types = conf.get_recipe('watchdog')  # 'watchdog' = 'watchdog' specified in .xml
FREQUENCY = 125  # send data in default 125Hz
con.send_output_setup(state_names, state_types, FREQUENCY)  # syncs output set-up with robot
setp = con.send_input_setup(setp_names, setp_types)  # syncs input set-up with robot
watchdog = con.send_input_setup(watchdog_names, watchdog_types)  # syncs watchdog input with robot

# initialization of inputs
setp.input_double_register_0 = 0
setp.input_double_register_1 = 0
setp.input_double_register_2 = 0
setp.input_double_register_3 = 0
setp.input_double_register_4 = 0
setp.input_double_register_5 = 0
setp.input_bit_registers0_to_31 = 0
watchdog.input_int_register_0 = 0

# starts data synchronization capabilities, and ends program if this fails
if not con.send_start():
    sys.exit()

# waits for user to ensure both .urp and .py files are running before exchanging data
while True:
    print('Boolean 1 is False, please click CONTINUE on the Polyscope')
    # check output_reg status to see if we proceed
    state = con.receive()
    con.send(watchdog)  # let robot know to proceed in mode 0 (or initializes watchdog reg)
    if state.output_bit_registers0_to_31 == True:
        print('Boolean 1 is True, Robot Program can proceed\n')
        break

# length-related definitions
scratches = 4  # number of scratches expected (only for testing purposes)
leeway = 0.02  # leeway length at the end
length = (scratches * 0.002) + leeway  # total length of all blanks to be tested (in m)
scratched_length = 0  # total length of metal scratched (in m)
done = 0  # switch variable to ensure sprayer/powder etc. are not activated more than once in fast loops

# arrays for data recording
force = np.array([])
position = np.array([])



# =======================================================================================================================
# initial grinding (mode 1)
watchdog.input_int_register_0 = 1
con.send(watchdog)
while True:  # Waiting for move to finish
    state = con.receive()
    con.send(watchdog)
    if not state.output_bit_registers0_to_31:
        print('Initial grinding finished.\n')
        break

# =======================================================================================================================
# Function to find the Arduino port
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "ACM" in str(port):
            return port.device
    return None

# Function to control the solenoid valves
def valve(command):
    serialInst.write(bytes(command, "utf-8"))
    time.sleep(0.1)  # Small delay to ensure command is sent
    print(5)
    if serialInst.in_waiting > 0:
        print(9)
        response = serialInst.readline().decode("utf-8").strip()
        print(response)
    if command == "exit":
        serialInst.close()
        print("Program ended")

# Find and connect to the Arduino
arduino_port = find_arduino_port()
# if arduino_port is None:
#     print("Arduino not found")
# else:
#     print(f"Connecting to Arduino on port {arduino_port}")
#     serialInst = serial.Serial(port=arduino_port, baudrate=9600, timeout=1)
#     time.sleep(2)  # Wait for the connection to establish
#     # Example usage`
#     valve("1")
#     time.sleep(2)
#     valve("3")
#     time.sleep(2)
#     valve("4")
#     time.sleep(2)
#     valve("exit")

# looping dipping and scratching
while True:
    # dipping (mode 2)
    watchdog.input_int_register_0 = 2
    con.send(watchdog)
    while True:
        state = con.receive()
        con.send(watchdog)
        if state.output_bit_registers0_to_31 == False:
            print('Dipping finished. \n')
            break

    # scratching (mode 3)
    i = 0
    while i < 3:
        i = i + 1
        done = 0

        watchdog.input_int_register_0 = 3
        con.send(watchdog)

        # activate("1") # strip feeder on/off
        if arduino_port is None:
            print("Arduino not found")
        else:
            print(f"Connecting to Arduino on port {arduino_port}")
            serialInst = serial.Serial(port=arduino_port, baudrate=9600, timeout=1)
            time.sleep(2)  # Wait for the connection to establish
            # Example usage`
            valve("1")
            time.sleep(2)
            valve("exit")

        keepRunning = True
        while keepRunning:  # Waiting for 1 scratch to finish
            state = con.receive()
            con.send(watchdog)

            if (state.output_bit_registers32_to_63 == 0) and (done == 0):
                # activate("3") # sprayer on
                if arduino_port is None:
                    print("Arduino not found")
                else:
                    print(f"Connecting to Arduino on port {arduino_port}")
                    serialInst = serial.Serial(port=arduino_port, baudrate=9600, timeout=1)
                    time.sleep(2)  # Wait for the connection to establish
                    # Example usage`
                    valve("3")
                    time.sleep(2)
                    valve("exit")

                print('Lubricant sprayed. \n')
                done = 1
            elif (state.output_bit_registers32_to_63 == 1) and (done == 1):
                # activate("4") # strip feeder on/off
                if arduino_port is None:
                    print("Arduino not found")
                else:
                    print(f"Connecting to Arduino on port {arduino_port}")
                    serialInst = serial.Serial(port=arduino_port, baudrate=9600, timeout=1)
                    time.sleep(2)  # Wait for the connection to establish
                    # Example usage`
                    valve("4")
                    time.sleep(2)
                    valve("exit")

                print('Lubricant spraying stopped. \n')
                done = 2
            elif (state.output_bit_registers32_to_63 == 0) and (done == 2):
                # print('Force recording.')
                state = con.receive()
                forceXYZ = state.actual_TCP_force[:3]
                posXYZ = state.actual_TCP_pose[:3]
                force = np.append(force, forceXYZ)
                position = np.append(position, posXYZ)
            # elif (state.output_bit_registers32_to_63 == 1) and (done == 2):
                # print('Force not recording.')

            if not state.output_bit_registers0_to_31:
                scratched_length = scratched_length + 0.002  # increments fed amount
                print('Scratch finished. \n')
                keepRunning = False
                break
        if scratched_length >= (length - leeway):
            break
    if scratched_length >= (length - leeway):
        break


# end grinding (mode 1)
watchdog.input_int_register_0 = 1
con.send(watchdog)
while True:  # Waiting for move to finish
    state = con.receive()
    con.send(watchdog)
    if state.output_bit_registers0_to_31 == False:
        print('End grinding finished.\n')
        break

# disconnect (mode 4)
watchdog.input_int_register_0 = 4
con.send(watchdog)
con.send_pause()  # pause sending the values
con.disconnect()  # disconnect from UR10

# data collection
force = force.reshape((len(force)//3), 3)
position = position.reshape((len(position)//3), 3)
plotNoScratch = len(force) // scratches
time = np.linspace(0, plotNoScratch*1/FREQUENCY, plotNoScratch)
time = time.reshape(len(time), 1)
headerList = ["Time", "Force X", "Force Y", "Force Z", "Postion X", "Position Y", "Position Z"]
for i in range(1,scratches+1):
    # scratch data for each scratch
    scratchData = np.concatenate((time,
                                  force[(i-1)*plotNoScratch:i*plotNoScratch],
                                   position[(i-1)*plotNoScratch:i*plotNoScratch]),
                                   axis=1)
    with open("scratch" + i + "file.csv") as file:
        writer = csv.writer(file)
        writer.writerow(headerList)
        writer.writerow(scratchData)