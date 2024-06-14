import serial
import serial.tools.list_ports
import threading
import time

class ESP32:
    def __init__(self):
        self.ser = None
        self.motor_PWM = 0
        self.brake_PWM = 0
        self.steering_degrees = 0
        self.child_pipe = None

    def get_parent_data(self,):
            while True:
                if self.child_pipe.poll(None):
                    data = self.child_pipe.recv()
                    self.motor_PWM = data["motor_PWM"]
                    self.brake_PWM = data["brake_PWM"]
                    self.steering_degrees = data["steering_degrees"]
                    self.write_Data(f'<{self.motor_PWM}, {self.brake_PWM}, {self.steering_degrees}>')
                    time.sleep(0.005)

    def connect(self, child_pipe):
        self.child_pipe = child_pipe
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

        parent_data_thread = threading.Thread(target=self.get_parent_data)
        parent_data_thread.start()
        # while True:
            # self.recv_from_arduino()
            # self.serial_monitor()

    def write_Data(self, data):
        # ser.write("<Kaas, 1, 1.23456>".encode())
        self.ser.write(data.encode())

    def serial_monitor(self,):
            cc=str(self.ser.readline())
            line = cc[2:][:-5]
            if line != "":
                print(line)

    def recv_from_arduino(self,):
        global startMarker, endMarker
        startMarker = '<'
        endMarker = '>'
        
        data = ""
        serialByte = '' # any value that is not an end- or startMarker
        
        # wait for the start character
        while self.ser.read().decode() != startMarker:
            time.sleep(0.001)
        
        # save data until the end marker is found
        while serialByte != endMarker:
            data = data + serialByte 
            serialByte = self.ser.read().decode()
        print(data)
        return data
