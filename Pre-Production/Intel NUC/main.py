from ESP import ESP32 
from YOLO_easyOCR.YOLOv8 import ObjectDetection
from lineDetection.lines import Detection
from multiprocessing import Process, Pipe
import easyocr
import threading
import os
import time

def drivingAlgorithm():
    global esp32ParentPipe
    global esp32Data
    global lineDetectionData
    global objectDetectionData
    global defaultSpeed
    global speedSignSpeed

    defaultSpeed = 10
    desSpeed = 5

    # print(lineDetectionData)
    # print(objectDetectionData)

    # esp32Data["brakePWM"] = lineDetectionData["segment"]
    # esp32ParentPipe.send(esp32Data)

    # outerMostRedLight = None
    # outerMostSign = None
    # redLights = []
    tempObData = objectDetectionData
    for i, c in enumerate(objectDetectionData.boxes.cls):
        match objectDetectionData.names[int(c)]:
            case "Red":
                if getOuterMostRedLight(i, c):
                    currentSpeed = desSpeed
                    # if (lineDetected):
                        # stop()
            case "Green":
                if getOuterMostGreenLight(i, c):
                    if speedSignSpeed is not None:
                        currentSpeed = speedSignSpeed
                    else:
                        currentSpeed = defaultSpeed

            case "Sign":
                if getOuterMostSign(i, c):
                    currentSpeed = speedSignSpeed
            
            case _:
                pass

def getOuterMostRedLight(i, c):
    outerMostRedLight = None
    redLights = []

    if objectDetectionData.names[int(c)] == "Red":  # Filter result based on class
        maxXCoord = objectDetectionData.boxes.xyxy[i][2]
        redLights.append(maxXCoord)
        if outerMostRedLight is None:
            outerMostRedLight = maxXCoord
        if maxXCoord > outerMostRedLight: outerMostRedLight = maxXCoord
        print(redLights)
        if outerMostRedLight is not None:
            print(outerMostRedLight)

def getOuterMostGreenLight(i, c):
    outerMostGreenLight = None
    greenLights = []

    if objectDetectionData.names[int(c)] == "Green":  # Filter result based on class
        maxXCoord = objectDetectionData.boxes.xyxy[i][2]
        greenLights.append(maxXCoord)
        if outerMostGreenLight is None:
            outerMostGreenLight = maxXCoord
        if maxXCoord > outerMostGreenLight: outerMostGreenLight = maxXCoord
        print(greenLights)
        if outerMostGreenLight is not None:
            print(outerMostGreenLight)

def getOuterMostSign(i, c):
    outerMostSign = None

    if objectDetectionData.names[int(c)] == "Green":
        signCoords = objectDetectionData.boxes.xyxy[i]
        if outerMostSign is None:
            outerMostSign = signCoords
        if signCoords[2] > outerMostSign[2]:  # compare x_max
            outerMostSign = signCoords
        if outerMostSign is not None:
            speedSignSpeed = ocrDetect(outerMostSign, objectDetectionData)
            print(speedSignSpeed)
            return speedSignSpeed

def ocrDetect(outerMostSign, result):
        x_min, y_min, x_max, y_max = outerMostSign
        roi = result.orig_img[int(y_min):int(y_max), int(x_min):int(x_max)]  # crop frame using bb cords
        for (bbox, text, prob) in easyOcrReader.readtext(roi):
            print(text)
            return text

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
    desSpeed = 0

    # esp32ParentPipe, esp32ChildPipe = Pipe()
    # esp32Process = Process(target=ESP32().connect, args=(esp32ChildPipe,), daemon=True)
    # esp32Process.start()

    yolov8ParentPipe, yolov8ChildPipe = Pipe()
    yolov8Process = Process(target=ObjectDetection().detect, args=(yolov8ChildPipe,), daemon=True)
    yolov8Process.start()
    yolov8DataThread = threading.Thread(target=getProcessData, args=(yolov8ParentPipe, "yolov8"), daemon=True)
    easyOcrReader = easyocr.Reader(['en'], gpu=False)
    yolov8DataThread.start()

    # lineDetectionParentPipe, lineDetectionChildPipe = Pipe()
    # lineDetectionProcess = Process(target=Detection().run, args=(lineDetectionChildPipe,), daemon=True)
    # lineDetectionProcess.start()
    # lineDetectionDataThread = threading.Thread(target=getProcessData, args=(lineDetectionParentPipe, "lineDetection"), daemon=True)
    # lineDetectionDataThread.start()
    
    # while lineDetectionData is None:
    #     time.sleep(0.01)

    while objectDetectionData is None:
        time.sleep(0.01)

    while True:
        drivingAlgorithm()
