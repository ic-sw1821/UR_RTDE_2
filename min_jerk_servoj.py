# imports
import sys
sys.path.append('')
import logging
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

import time
from matplotlib import pyplot as plt

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

# establish TCP/IP connection with robot
ROBOT_HOST = '192.168.1.10'
ROBOT_PORT = 30004
logging.getLogger().setLevel(logging.INFO) # generates log of how the robot did for debugging
con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
connection_state = con.connect()
while connection_state != 0:
    time.sleep(0.5)
    connection_state = con.connect()
print("Remote connection has been established with UR10. \n")
con.get_controller_version() # get controller version

# sync I/O settings from .xml with robot
config_filename = 'control_loop_configuration.xml'  # specify xml file for data synchronization
conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe('state')  # 'state' = outputs specified in .xml
setp_names, setp_types = conf.get_recipe('setp')  # 'setp' = inputs specified in .xml
watchdog_names, watchdog_types= conf.get_recipe('watchdog') # 'watchdog' = 'watchdog' specified in .xml
FREQUENCY = 125  # send data in default 125Hz
con.send_output_setup(state_names, state_types, FREQUENCY) # syncs output set-up with robot
setp = con.send_input_setup(setp_names, setp_types) # syncs input set-up with robot
watchdog = con.send_input_setup(watchdog_names, watchdog_types) # syncs watchdog input with robot

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
start_pose = [0.62899, -0.03993, 0.08944, 3.1415, 0.0001, 0.0001] # scratch 1
desired_pose = [0.69436, 0.17108, -0.08862, 3.1416, 0.0000, 0.0002] # scratch 2

# waits for user to ensure both .urp and .py files are running before exchanging data
while True:
    print('Boolean 1 is False, please click CONTINUE on the Polyscope')
    # check output_reg status to see if we proceed
    state = con.receive()
    con.send(watchdog)  # let robot know to proceed in mode 0 (or initializes watchdog reg)
    if state.output_bit_registers0_to_31 == True:
        print('Boolean 1 is True, Robot Program can proceed\n')
        break

length = 0.026 # total length of all blanks to be tested (in m)
scratched_length = 0 # total length of metal scratched (in m)

# initial grinding (mode 1)
watchdog.input_int_register_0 = 1
con.send(watchdog)
while True: # Waiting for move to finish
    state = con.receive()
    con.send(watchdog)
    if state.output_bit_registers0_to_31 == False:
        print('Proceeding\n')
        break

# main infinite operations loop
while True: # Waiting for move to finish
    # Dipping (mode 2)
    watchdog.input_int_register_0 = 2
    con.send(watchdog)
    while True:
        state = con.receive()
        con.send(watchdog)

        if state.output_bit_registers32_to_63 == False:
            # valve.powder()
            print('Powdering\n')

        if state.output_bit_registers0_to_31 == False:
            print('Proceeding\n')
            break

    # Scratching (mode 3)
    i = 0
    while i<3:
        i = i + 1

        # valve.feed()
        time.sleep(0.3)

        watchdog.input_int_register_0 = 3
        con.send(watchdog)

        # valve.spray(1)

        while True:  # Waiting for 1 scratch to finish
            state = con.receive()
            con.send(watchdog)

            if state.actual_TCP_pose[2] > 0.3:
                # valve.spray(0)
                print('Spray off\n')

            if state.output_bit_registers0_to_31 == False:
                # valve.spray(0)
                scratched_length = scratched_length + 0.002  # increments fed amount
                print('Proceeding\n')
                break
        if scratched_length >= (length-0.02):
            break
    if scratched_length >= (length-0.02):
        break

# initial grinding (mode 1)
watchdog.input_int_register_0 = 1
con.send(watchdog)
while True: # Waiting for move to finish
    state = con.receive()
    con.send(watchdog)
    if state.output_bit_registers0_to_31 == False:
        print('Proceeding\n')
        break

# mode 4 - end of operation
watchdog.input_int_register_0 = 4
con.send(watchdog)
con.send_pause() # pause sending the values
con.disconnect() # disconnect from UR10

# list_to_setp(setp, start_pose)  # store start_pose in setp format
# con.send(setp) # pass setp to .urp program to execute on robot

