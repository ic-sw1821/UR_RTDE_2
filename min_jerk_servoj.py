# ------------- Imports -------------
import sys
sys.path.append('')
import logging
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

import time
from matplotlib import pyplot as plt
from min_jerk_planner_translation import PathPlanTranslation


# ------------- Functions -------------
# reads the set-point that was just sent (likely the robot's current pos)
def setp_to_list(setp):
    temp = []
    for i in range(0, 6):
        temp.append(setp.__dict__["input_double_register_%i" % i])
    return temp

# writes our desired set-point to suitable format to be communicated
def list_to_setp(setp, list):
    for i in range(0, 6):
        setp.__dict__["input_double_register_%i" % i] = list[i]
    return setp


# ------------- Ethernet -------------
ROBOT_HOST = '192.168.1.10' # Found in system network - IP-address
ROBOT_PORT = 30004
config_filename = 'control_loop_configuration.xml'  # specify xml file for data synchronization

# keep_running = True, keep or delete?

logging.getLogger().setLevel(logging.INFO) # generates log of how the robot did for debugging

# reformat I/O settings from XML to Python-friendly format
conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe('state')  # Define recipe for access to robot output ex. joints,tcp etc.
setp_names, setp_types = conf.get_recipe('setp')  # Define recipe for access to robot input
watchdog_names, watchdog_types= conf.get_recipe('watchdog')


# ------------- Connection (no change needed) -------------
# establishes connection
con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
connection_state = con.connect()

# check if connection has been established
while connection_state != 0:
    time.sleep(0.5)
    connection_state = con.connect()
print("---------------Successfully connected to the robot-------------\n")

# get controller version
con.get_controller_version()

# ------------------- Communications (no change needed) ----------------------------
FREQUENCY = 500  # send data in 500 Hz instead of default 125Hz

# allows us to receive from the robot
con.send_output_setup(state_names, state_types, FREQUENCY)
# configure an input package that the external application will send to the robot controller
setp = con.send_input_setup(setp_names, setp_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)

# ------------------- Communications (change if .xml is changed) -------------------
# initialization of registers, add more if you use more reigsters
setp.input_double_register_0 = 0
setp.input_double_register_1 = 0
setp.input_double_register_2 = 0
setp.input_double_register_3 = 0
setp.input_double_register_4 = 0
setp.input_double_register_5 = 0

setp.input_bit_registers0_to_31 = 0
# watchdog used in .urp file to ensure the Python code is running in sync
watchdog.input_int_register_0 = 0

# start data synchronization
if not con.send_start():
    sys.exit()

# Defining key points ============================================================
# first 3 values are xyz, last 3 are orientations
start_pose = [0.62899, -0.03993, 0.08944, 3.1415, 0.0001, 0.0001]
desired_pose = [0.69436, 0.17108, -0.08862, 3.1416, 0.0000, 0.0002]

orientation_const = start_pose[3:]

# Prints the initial pose of the tool
state = con.receive()
tcp1 = state.actual_TCP_pose
print(tcp1)

#   ------------  mode = 1 (Connection) -----------
# control loop to establish connection with robot
while True:
    print('Boolean 1 is False, please click CONTINUE on the Polyscope')
    # receives our outputs-of-interest from robot
    state = con.receive()
    # add our output states of interest here?
    # e.g. s1 = state.actual_TCP_pose above

    # kick watchdog
    con.send(watchdog)
    # print(f"runtime state is {state.runtime_state}")
    if state.output_bit_registers0_to_31 == True:
        print('Boolean 1 is True, Robot Program can proceed to mode 1\n')
        break

print("-------Executing moveJ -----------\n")


watchdog.input_int_register_0 = 1
con.send(watchdog)  # sending mode == 1
list_to_setp(setp, start_pose)  # changing initial pose to setp
con.send(setp) # sending initial pose

while True:
    print('Waiting for movej() to finish')
    state = con.receive()
    con.send(watchdog)
    if state.output_bit_registers0_to_31 == False:
        print('Proceeding to mode 2\n')
        break


print("-------Executing servoJ  -----------\n")
watchdog.input_int_register_0 = 2
con.send(watchdog)  # sending mode == 2

trajectory_time = 8  # time of min_jerk trajectory
dt = 1/500  # 500 Hz    # frequency
plotter = True

# ------------------ Control loop initialization -------------------------

planner = PathPlanTranslation(start_pose, desired_pose, trajectory_time)
# ----------- minimum jerk preparation -----------------------


if plotter:
    time_plot = []

    min_jerk_x = []
    min_jerk_y = []
    min_jerk_z = []

    min_jerk_vx = []
    min_jerk_vy = []
    min_jerk_vz = []

    px = []
    py = []
    pz = []

    vx = []
    vy = []
    vz = []

#   -------------------------Control loop --------------------
state = con.receive()
tcp = state.actual_TCP_pose
t_current = 0
t_start = time.time()

while time.time() - t_start < trajectory_time:
    t_init = time.time()
    state = con.receive()
    t_prev = t_current
    t_current = time.time() - t_start

    print(f"dt:{t_current-t_prev}")
    # read state from the robot
    if state.runtime_state > 1:
        #   ----------- minimum_jerk trajectory --------------
        if t_current <= trajectory_time:
            [position_ref, lin_vel_ref, acceleration_ref] = planner.trajectory_planning(t_current)

        # ------------------ impedance -----------------------
        current_pose = state.actual_TCP_pose
        current_speed = state.actual_TCP_speed

        pose = position_ref.tolist() + orientation_const

        list_to_setp(setp, pose)
        con.send(setp)

        if plotter:
            time_plot.append(time.time() - t_start)

            min_jerk_x.append(position_ref[0])
            min_jerk_y.append(position_ref[1])
            min_jerk_z.append(position_ref[2])

            min_jerk_vx.append(lin_vel_ref[0])
            min_jerk_vy.append(lin_vel_ref[1])
            min_jerk_vz.append(lin_vel_ref[2])

            px.append(current_pose[0])
            py.append(current_pose[1])
            pz.append(current_pose[2])

            vx.append(current_speed[0])
            vy.append(current_speed[1])
            vz.append(current_speed[2])

print(f"It took {time.time()-t_start}s to execute the servoJ")
print(f"time needed for min_jerk {trajectory_time}\n")

state = con.receive()
print('--------------------\n')
print(state.actual_TCP_pose)

# ====================mode 3===================
watchdog.input_int_register_0 = 3

# watchdogs are used so one program waits for the other to finish before executing more code
con.send(watchdog)

# pause sending the values
con.send_pause()
# disconnect from UR10
con.disconnect()


if plotter:
    # ----------- position -------------
    plt.figure()
    plt.plot(time_plot, min_jerk_x, label="x_min_jerk")
    plt.plot(time_plot, px, label="x_robot")
    plt.legend()
    plt.grid()
    plt.ylabel('Position in x[m]')
    plt.xlabel('Time [sec]')

    plt.figure()
    plt.plot(time_plot, min_jerk_y, label="y_min_jerk")
    plt.plot(time_plot, py, label="y_robot")
    plt.legend()
    plt.grid()
    plt.ylabel('Position in y[m]')
    plt.xlabel('Time [sec]')

    plt.figure()
    plt.plot(time_plot, min_jerk_z, label="z_min_jerk")
    plt.plot(time_plot, pz, label="z_robot")
    plt.legend()
    plt.grid()
    plt.ylabel('Position in z[m]')
    plt.xlabel('Time [sec]')

    # ----------- velocity -------------
    plt.figure()
    plt.plot(time_plot, min_jerk_vx, label="vx_min_jerk")
    plt.plot(time_plot, vx, label="vx_robot")
    plt.legend()
    plt.grid()
    plt.ylabel('Velocity [m/s]')
    plt.xlabel('Time [sec]')

    plt.figure()
    plt.plot(time_plot, min_jerk_vy, label="vvy_min_jerk")
    plt.plot(time_plot, vy, label="vy_robot")
    plt.legend()
    plt.grid()
    plt.ylabel('Velocity [m/s]')
    plt.xlabel('Time [sec]')

    plt.figure()
    plt.plot(time_plot, min_jerk_vz, label="vz_min_jerk")
    plt.plot(time_plot, vz, label="vz_robot")
    plt.legend()
    plt.grid()
    plt.ylabel('Velocity [m/s]')
    plt.xlabel('Time [sec]')
    plt.show()