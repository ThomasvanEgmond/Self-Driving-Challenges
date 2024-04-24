from ESP import ESP32 
from YOLO_easyOCR.YOLOv8 import ObjectDetection
from lineDetection.lines import Detection
from multiprocessing import Process, Pipe
import threading
import os
import time

def drivingAlgorithm():
    global esp32ParentPipe
    global esp32Data
    global lineDetectionData
    global objectDetectionData

    print(lineDetectionData)
    print(objectDetectionData)

    # esp32Data["brakePWM"] = lineDetectionData["segment"]
    esp32ParentPipe.send(esp32Data)


def getProcessData(parentPipe, process):
    while True:
        if parentPipe.poll(None):
            data = parentPipe.recv()
            # print(data)
            match process:
                case "lineDetection":
                    global lineDetectionData
                    lineDetectionData = data
                case "yolov8":
                    global objectDetectionData
                    objectDetectionData = data


if __name__ == '__main__':
    pass
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    esp32Data = {
        "motorPWM": 0,
        "brakePWM": 0,
        "steeringDegrees": 90,
        "state": "driving"
    }

    lineDetectionData = None
    objectDetectionData = None

    esp32ParentPipe, esp32ChildPipe = Pipe()
    esp32Process = Process(target=ESP32().connect, args=(esp32ChildPipe,), daemon=True)
    esp32Process.start()

    yolov8ParentPipe, yolov8ChildPipe = Pipe()
    yolov8Process = Process(target=ObjectDetection().detect, args=(yolov8ChildPipe,), daemon=True)
    yolov8Process.start()
    yolov8DataThread = threading.Thread(target=getProcessData, args=(yolov8ParentPipe, "yolov8"), daemon=True)
    yolov8DataThread.start()

    lineDetectionParentPipe, lineDetectionChildPipe = Pipe()
    lineDetectionProcess = Process(target=Detection().run, args=(lineDetectionChildPipe,), daemon=True)
    lineDetectionProcess.start()
    lineDetectionDataThread = threading.Thread(target=getProcessData, args=(lineDetectionParentPipe, "lineDetection"), daemon=True)
    lineDetectionDataThread.start()
    
    while lineDetectionData is None:
        time.sleep(0.01)

    while objectDetectionData is None:
        time.sleep(0.01)

    while True:
        drivingAlgorithm()
