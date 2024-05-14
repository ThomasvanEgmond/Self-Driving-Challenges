import serial
import serial.tools.list_ports
import threading
import time

class ESP32:
    def __init__(self):
        self.ser = None
        self.motorPWM = 0
        self.brakePWM = 0
        self.steeringDegrees = 0
        self.childPipe = None

    def getParentData(self,):
            while True:
                if self.childPipe.poll(None):
                    data = self.childPipe.recv()
                    self.motorPWM = data["motorPWM"]
                    self.brakePWM = data["brakePWM"]
                    self.steeringAngle = data["steeringAngle"]
                    # self.writeData(f'<{self.motorPWM}, {self.brakePWM}, {self.steeringDegrees}, {self.state}>')
                    timeInSeconds = round(time.time() - 1682249887 - 31623000, 3)
                    # print(timeInSeconds)
                    # self.writeData(f'<{int(timeInSeconds)}, {int(timeInSeconds)- 300}, {timeInSeconds - 300}, moe>')
                    self.writeData(f'<{self.motorPWM}, {self.brakePWM}, {self.steeringAngle}>')

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
            self.recvFromArduino()
            # self.serialMonitor()

    def writeData(self, data):
        # ser.write("<Kaas, 1, 1.23456>".encode())
        self.ser.write(data.encode())

    def serialMonitor(self,):
            cc=str(self.ser.readline())
            line = cc[2:][:-5]
            if line != "":
                print(line)

    def recvFromArduino(self,):
        global startMarker, endMarker
        startMarker = '<'
        endMarker = '>'
        
        data = ""
        serialByte = '' # any value that is not an end- or startMarker
        
        # wait for the start character
        while self.ser.read().decode() != startMarker:
            pass
            # x = self.ser.read().decode()
            # print(x)
        
        # save data until the end marker is found
        while serialByte != endMarker:
            data = data + serialByte 
            serialByte = self.ser.read().decode()
        print(data)
        return data
