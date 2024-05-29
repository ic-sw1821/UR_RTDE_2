 # Arduino integration


import serial.tools.list_ports


ports = serial.tools.list_ports.comports()  # opens comports
serialInst = serial.Serial()
print(5)
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
def valve():
    print(5)
    while True:
        command = input("Enter command: ")
        serialInst.write(command.encode("utf-8"))

        if command == "exit":
            print("Program ended")
            quit()

valve()