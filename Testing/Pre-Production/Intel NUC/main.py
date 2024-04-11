import serial
import serial.tools.list_ports
from lijndetection.lines import Detection
from multiprocessing import Process

def start():
    print('Searching for connected ESP32...')
    lineDetectionObject = Detection()
    lineDetectionObject.run()
    ser = None
    while ser is None:
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

    ser.flushInput()
    ser.flushOutput()
    print('Connected to ' + ser.name)

    # Send data to ESP32
    data_to_send = "<Kaas, 1, 1.23456>"
    ser.write("<Kaas, 1, 1.23456>".encode())

    linedetectionProcess = Process()


    # Close the serial connection
    ser.close()

if __name__ == '__main__':
    start()