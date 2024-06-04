# Imports
# imports needed for UR10 connection
import sys
sys.path.append('')
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

# imports needed for other purposes
import time
import datetime
import numpy as np
import pandas as pd
import serial.tools.list_ports


# =======================================================================================================================
# User Inputs
lube_mode = 1 # 1 for sprayer, 2 for dipper
scratches = 3  # number of scratches expected (only for testing purposes)
leeway = 0.02  # leeway length at the end
length = (scratches * 0.002) + leeway  # total length of all blanks to be tested (in m)


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
    print(1)
    serialInst.write(bytes(command, "utf-8"))
    # time.sleep(0.1)  # Small delay to ensure command is sent
    print('Written to Arduino, reading for response.')
    bytesReceived = False
    while bytesReceived == False:
        if serialInst.in_waiting > 0:
            response = serialInst.readline().decode("utf-8").strip()
            end = time.time()
            # print("Arduino Activation Time: ", end - start)
            print(response)
            bytesReceived = True
        if command == "exit":
            end = time.time()
            print("end:", end - start)
            serialInst.close()
            print("Program ended")
            bytesReceived = True

# Find and connect to the Arduino
arduino_port = find_arduino_port()
if arduino_port is None:
    print("Arduino not found")
else:
    print(f"Connecting to Arduino on port {arduino_port}")
    serialInst = serial.Serial(port=arduino_port, baudrate=112500, timeout=None)
    time.sleep(2)  # Wait for the connection to establish


# =======================================================================================================================
# waits for user to ensure both .urp and .py files are running before exchanging data
while True:
    print('Please turn on pressured air, and wait for the valves to click before pressing CONTINUE on the Polyscope!')
    # check output_reg status to see if we proceed
    state = con.receive()
    con.send(watchdog)  # let robot know to proceed in mode 0 (or initializes watchdog reg)
    if state.output_bit_registers0_to_31 == True:
        print('Arduino initialized, robot starting!\n')
        # time.sleep(1)
        break


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

# looping dipping and scratching
scratch_count = 0  # counter for finished scratches (for printing)
scratched_length = 0  # total length of metal scratched (in m)
force = np.array([])  # arrays for data recording
position = np.array([]) # arrays for data recording

while True:
    if lube_mode == 2:
        # dipping (mode 2)
        watchdog.input_int_register_0 = 2
        con.send(watchdog)
        valve("6") # on/off powder spray routine
        while True:
            state = con.receive()
            con.send(watchdog)
            if state.output_bit_registers0_to_31 == False:
                print('Dipping finished. \n')
                break

    # scratching (mode 3)
    scratch_count = scratch_count + 1
    done = 0
    startCycle = time.time()
    watchdog.input_int_register_0 = 3
    con.send(watchdog)
    valve("3")
    start = time.time()
    # CHANGE
    # if lube_mode == 1:
    #     valve("3")
    #     valve("1")
    # elif lube_mode == 2:
    #     valve("6")
    # valve("1")
    keepRunning = True
    while keepRunning and scratches > 0:  # Waiting for 1 scratch to finish
        # valve("3")
        state = con.receive()
        con.send(watchdog)
        if (state.output_bit_registers32_to_63 == 0) and done == 0:
            print('Force recording.')
            state = con.receive()
            forceXYZ = state.actual_TCP_force[:3]
            posXYZ = state.actual_TCP_pose[:3]
            force = np.append(force, forceXYZ)
            position = np.append(position, posXYZ)
            done = 1
            print(done)

        if not state.output_bit_registers0_to_31:
            scratched_length = scratched_length + 0.002  # increments fed amount
            print(str(scratch_count) + 'th scratch finished. \n')
            valve("1")
            keepRunning = False
            done = 0
            break
    endCycle = time.time()
    print(endCycle - startCycle)
    if scratched_length >= (length - leeway): # restore leeway consideration during calculation
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
# force = force.reshape((len(force)//3), 3)
# position = position.reshape((len(position)//3), 3)
# plotNoScratch = len(force) // scratch_count
# time = np.linspace(0, plotNoScratch*1/FREQUENCY, plotNoScratch)
# time = time.reshape(len(time), 1)
# headerList = ["Time", "Force X", "Force Y", "Force Z", "Postion X", "Position Y", "Position Z"]
# for i in range(1, scratch_count + 1):
#     # scratch data for each scratch
#     scratchData = np.concatenate((time,
#                                   force[(i-1)*plotNoScratch:i*plotNoScratch],
#                                    position[(i-1)*plotNoScratch:i*plotNoScratch]),
#                                    axis=1)
#     scratchData = np.append([headerList], scratchData, axis=0)
#     df = pd.DataFrame(scratchData)
#     name = datetime.datetime.now().replace("/", "-") + " Scratch" + str(i) + "file.csv"
#     df.to_csv(name, index=False)
