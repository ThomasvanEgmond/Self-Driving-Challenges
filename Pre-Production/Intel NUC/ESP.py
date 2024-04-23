import serial
import serial.tools.list_ports
import threading
import time

class ESP32:
    def __init__(self):
        self.ser = None
        self.motorPWM = 0
        self.brakePWM = 0
        self.steeringDegrees = 90
        self.state = "driving"
        self.childPipe = None

    def getParentData(self,):
            while True:
                if self.childPipe.poll(None):
                    data = self.childPipe.recv()
                    self.motorPWM = data["motorPWM"]
                    self.brakePWM = data["brakePWM"]
                    self.steeringDegrees = data["steeringDegrees"]
                    self.state = data["state"]
                    # self.writeData(f'<{self.motorPWM}, {self.brakePWM}, {self.steeringDegrees}, {self.state}>')
                    timeInSeconds = round(time.time() - 1682249887 - 31623000, 3)
                    # print(timeInSeconds)
                    # self.writeData(f'<{int(timeInSeconds)}, {int(timeInSeconds)- 300}, {timeInSeconds - 300}, moe>')
                    self.writeData(f'<{self.motorPWM}, {self.brakePWM}, {self.steeringDegrees}, {self.state}>')

                    time.sleep(0.005)

                    # print(data)
                    # match process:
                    #     case "lineDetection":
                    #         global lineDetectionData
                    #         lineDetectionData = data
                    #     case "yolov8":
                    #         global objectDetectionData
                    #         objectDetectionData = data

    def connect(self, childPipe):
        self.childPipe = childPipe
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

        parentDataThread = threading.Thread(target=self.getParentData)
        parentDataThread.start()
        while True:
            self.receiveData()

    def writeData(self, data):
        # ser.write("<Kaas, 1, 1.23456>".encode())
        self.ser.write(data.encode())

    def receiveData(self,):
            cc=str(self.ser.readline())
            line = cc[2:][:-5]
            if line != "":
                print(line)
            # print(self.ser.readline())
