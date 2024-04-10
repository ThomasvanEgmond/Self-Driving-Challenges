import os
import sys
import time
import serial
import serial.tools.list_ports

print('Search...')
ports = serial.tools.list_ports.comports(include_links=False)
while not ports:
    ports = serial.tools.list_ports.comports(include_links=False)
for port in ports :
    print('Find port '+ port.device)


while True:
    try:
        ser = serial.Serial(port.device)
        if ser.isOpen():
            ser.close()
        ser = serial.Serial(port.device, 115200, timeout=1)
        break
    except BaseException as e:
        pass
ser.flushInput()
ser.flushOutput()
print('Connect ' + ser.name)

# Open serial connection to ESP32
# ser = serial.Serial('COM6', 115200)  # Replace 'COMX' with your ESP32's serial port
# print("Serial Port Connected")

# Send data to ESP32
data_to_send = "<Kaas, 1, 1.23456>"
ser.write("<Kaas, 1, 1.23456>".encode())

# Close the serial connection
ser.close()
