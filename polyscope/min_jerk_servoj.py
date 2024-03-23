# imports
import sys

sys.path.append('')
import logging
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import rtde.csv_writer as csvWriter

import time
from matplotlib import pyplot as plt
import numpy as np

import serial.tools.list_ports

# functions for writing set-points to the robot
# converts the .xml setp format sent and converts it back into Python form
def setp_to_list(setp):
    temp = []
    for i in range(0, 6):
        temp.append(setp.__dict__["input_double_register_%i" % i])
    return temp

    # writes Python array-form coordinates into .xml setp format to be sent to robot with con.send(setp)


def list_to_setp(setp, list):
    for i in range(0, 6):
        setp.__dict__["input_double_register_%i" % i] = list[i]
    return setp

# establish TCP/IP connection with robot (mode 0)
ROBOT_HOST = '192.168.1.10'
ROBOT_PORT = 30004
logging.getLogger().setLevel(logging.INFO)  # generates log of how the robot did for debugging
con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
connection_state = con.connect()
while connection_state != 0:
    time.sleep(0.5)
    connection_state = con.connect()
print("Robot connected. \n")
con.get_controller_version()  # get controller version

# sync I/O settings from .xml with robot
config_filename = '../control_loop_configuration.xml'  # specify xml file for data synchronization
conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe('state')  # 'state' = outputs specified in .xml
setp_names, setp_types = conf.get_recipe('setp')  # 'setp' = inputs specified in .xml
watchdog_names, watchdog_types = conf.get_recipe('watchdog')  # 'watchdog' = 'watchdog' specified in .xml
# output_names, output_types = conf.get_recipe('out')
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

# first 3 values are xyz, last 3 are orientations
start_pose = [0.62899, -0.03993, 0.08944, 3.1415, 0.0001, 0.0001]  # scratch 1
desired_pose = [0.69436, 0.17108, -0.08862, 3.1416, 0.0000, 0.0002]  # scratch 2

# Arduino integration
ports = serial.tools.list_ports.comports()  # opens comports
serialInst = serial.Serial()

portsList = []
for each in ports:  # reads each port into a list
    portsList.append(str(each))
    print(str(each))

for i in range(len(portsList)):  # finds the port the arduino is linked to
    if "Arduino" in portsList[i]:
        use = portsList[i].split()[0]
        print(use)

serialInst.baudrate = 9600
serialInst.port = use  # assigns the arduino port to
serialInst.open()

# function to control the solenoid valves for the pneumatic strip feeder and the sprayer
def valve(command):
    while True:
        command = input("Enter command: ")
        serialInst.write(command.encode("utf-8"))

        if command == "exit":
            print("Program ended")
            quit()


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
scratches = 4 # number of scratches expected (only for testing purposes)
leeway = 0.02  # leeway length at the end
length = (scratches * 0.002) + leeway  # total length of all blanks to be tested (in m)
scratched_length = 0  # total length of metal scratched (in m)
done = 0  # switch variable to ensure sprayer/powder etc. are not activated more than once in fast loops

# initial grinding (mode 1)
watchdog.input_int_register_0 = 1
con.send(watchdog)
while True:  # Waiting for move to finish
    state = con.receive()
    con.send(watchdog)
    if not state.output_bit_registers0_to_31:
        print('Initial grinding finished.\n')
        break

force = np.empty((scratches, 1))
position = np.empty((scratches, 1))

# looping dipping and scratching
while True:
    # dipping (mode 2)
    watchdog.input_int_register_0 = 2
    con.send(watchdog)
    done = 0
    while True:
        state = con.receive()
        con.send(watchdog)

        if (not state.output_bit_registers32_to_63) and (done == 0):
            # valve.powder()
            valve(5)
            print('Powder sprayed. \n')
            done = 1

        if state.output_bit_registers0_to_31 == False:
            print('Dipping finished. \n')
            break

    # scratching (mode 3)
    i = 0
    while i < 3:
        i = i + 1
        done = 0

        # valve(1) # feeds by 0.002 mm
        time.sleep(0.5)

        watchdog.input_int_register_0 = 3
        con.send(watchdog)

        # valve(3) # turns on spray
        keepRunning = True
        while keepRunning:  # Waiting for 1 scratch to finish
            state = con.receive()
            con.send(watchdog)

            state = con.receive() 
            if state is not None:
                forceXY = state.actual_TCP_force[:1]
                posX = state.actual_TCP_pose[0]
                force[scratched_length//0.002] = np.append(force[scratched_length//0.002], forceXY)
                position[scratched_length//0.002] = np.append(position[scratched_length//0.002], posX)
            
            if (state.actual_TCP_pose[2] > 0.3) and (done == 0):
                # valve.spray(0)
                # valve(4)
                print('Lubricant sprayed. \n')
                done = 1

            if not state.output_bit_registers0_to_31:
                # valve.spray(0)
                # valve(4)
                scratched_length = scratched_length + 0.002  # increments fed amount
                print('Scratch finished. \n')
                keepRunning = False
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

force.tofile("Force data.csv", sep = ",")
position.tofile("Postion data.csv", sep = ",")

# disconnect (mode 4)
watchdog.input_int_register_0 = 4
con.send(watchdog)
con.send_pause()  # pause sending the values
con.disconnect()  # disconnect from UR10

# list_to_setp(setp, start_pose)  # store start_pose in setp format
# con.send(setp) # pass setp to .urp program to execute on robot



