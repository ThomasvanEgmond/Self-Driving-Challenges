import serial
import serial.tools.list_ports

print('Searching for connected ESP32...')

while True:
    ser = None
    ports = serial.tools.list_ports.comports(include_links=False)
    for port in ports:
        print('Found port '+ port.device)
        try:
            ser = serial.Serial(port.device)
            if ser.isOpen():
                ser.close()
            ser = serial.Serial(port.device, 115200, timeout=1)
            break
        except BaseException as e:
            print("Failed to connect to " + port.device)
            # print(e)
            continue
    if ser is not None:
        ser.flushInput()
        ser.flushOutput()
        print('Connected to ' + ser.name)
        break

# Send data to ESP32
data_to_send = "<Kaas, 1, 1.23456>"
ser.write("<Kaas, 1, 1.23456>".encode())

# Close the serial connection
ser.close()
