## UR_RTDE_2
Implementation of RTDE integration with UR10 and serial-comms with Arduino for 2023-24 UltraMan DMT project.

#### --- What are the files in this repository? ---
`control_loop_configuration.xml`: contains list of the registers to be read and overwritten.

`TheChosen3.py`: main Python code for coordinating with .urp code and Arduino.

`min_jerk_servoj.py`: main script responsible for communication with the robot. It communicates with packages stored in **rtde** folder so make sure you download all the required files.

__polyscope__: contains urp file that can be uploaded to the robot
__rtde__: contains all the files needed for RTDE communication taken from: 
https://www.universal-robots.com/articles/ur/interface-communication/real-time-data-exchange-rtde-guide/

#### --- How to run the program? ---
After downloading the rtde folder as well as all the python packages in this repositiory upload the urp. file to the robot.
1) Run the urp file on the robot till a "Continue" button appears
2) Run the python script
3) Click "Continue" on the polyscope

#### Extras: 
 Below you can find the simplified description of our task as explained in the youtube video: 
![graph](https://user-images.githubusercontent.com/72759092/128363193-1e1929cd-c6dc-430f-9e93-6e97f150e4e4.jpg)

