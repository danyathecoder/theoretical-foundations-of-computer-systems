import serial

port1 = serial.Serial("com_interface1")
port2 = serial.Serial("com_interface2")
print("Port 1 is open: {}". format(port1.isOpen()))
print("Port 2 is open: {}". format(port2.isOpen()))
