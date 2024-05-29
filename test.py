 # Arduino integration

import serial.tools.list_ports

ports = serial.tools.list_ports.comports()  # opens comports
portsList = []
for each in ports:  # reads each port into a list
    portsList.append(str(each))
    print(str(each))
print(portsList)
for i in range(len(portsList)):  # finds the port the arduino is linked to
    if "ACM" in portsList[i]:
        use = portsList[i].split()[0]
        print(use)

serialInst = serial.Serial(baudrate=9600, port=use)
serialInst.open()

# function to control the solenoid valves for the pneumatic strip feeder and the sprayer
def valve():
    while True:
        command = input("Enter command: ")
        serialInst.write(bytes(command, "utf-8"))

        if command == "exit":
            serialInst.close()
            print("Program ended")
            quit()
    

valve()