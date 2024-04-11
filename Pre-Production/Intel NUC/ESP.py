import serial
import serial.tools.list_ports

class ESP32:
    def __init__(self):
        self.ser = None

    def connect(self, ):
        print('Searching for connected ESP32...')
        self.ser = None
        while self.ser is None:
            ports = serial.tools.list_ports.comports(include_links=False)
            for port in ports:
                print('Found port '+ port.device)
                try:
                    self.ser = serial.Serial(port.device)
                    if self.ser.isOpen():
                        self.ser.close()
                    self.ser = serial.Serial(port.device, 115200, timeout=1)
                    break
                except BaseException as e:
                    print("Failed to connect to " + port.device)
                    # print(e)
                    continue

        self.ser.flushInput()
        self.ser.flushOutput()
        print('Connected to ' + self.ser.name)

    def writeData(self, data):
        self.ser.write(data.encode())

    def receiveData(self, ):
        pass
