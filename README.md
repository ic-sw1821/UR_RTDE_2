## Repository: UR_RTDE_2
This repository contains a robust Python implementation of RTDE-integration with UR10 and serial-comms with Arduino, developed as a part of the 2023-24 UltraMan DMT project at Imperial College.

#### --- What are the files in this repository? ---
`DMT08b_9.urp`: URScript to be transfered and ran on the UR10's teaching-pendent.

'arduino_code.ino': Arduino code to be uploaded to the Arduino via the Arduino IDE.

`rtde (folder)`: contains all the files needed for RTDE communication taken from: 
https://www.universal-robots.com/articles/ur/interface-communication/real-time-data-exchange-rtde-guide/

`control_loop_configuration.xml`: contains list of the registers to be read and overwritten.

`TheChosen3.py`: the main Python code for coordinating with .urp code and Arduino to be run in the folder.

#### --- How to run the program? ---
After downloading the rtde folder as well as all the python packages in this repositiory, uploading the urp file to the robot, and storing the ino code on the Arduino:
1) Run the urp file on the robot till a "Continue" button appears
2) Run the python script
3) Click "Continue" on the polyscope
4) Try to look utterly unimpressed whilst the audience gushes and squeals around you
