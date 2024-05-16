from ESP import ESP32 
from YOLO_easyOCR.YOLOv8 import ObjectDetection
from lineDetection.lines import Detection
from multiprocessing import Process, Pipe
import easyocr
import threading
import os
import time

def drivingAlgorithm():
    parsedData = parseObjectDetectionData()
    if parsedData["outerMostRedLight"] is not None:
        print("joeppie")

def parseObjectDetectionData():
    outerMostRedLight = 0
    outerMostGreenLight = 0
    outerMostSign = 0

    for i, c in enumerate(objectDetectionData.boxes.cls):
        coords = objectDetectionData.boxes.xyxy[i]
        maxXCoord = coords[2]
        match objectDetectionData.names[int(c)]:
            case "Red":
                if maxXCoord > outerMostRedLight: outerMostRedLight = maxXCoord

            case "Green":
                if maxXCoord > outerMostGreenLight: outerMostGreenLight = maxXCoord
            
            case "Sign":   
                if outerMostSign is None:
                    outerMostSign = coords
                if maxXCoord > outerMostSign[2]:         # compare x_max
                    outerMostSign = coords



    if outerMostSign is not None:
        signSpeed = ocrDetect(outerMostSign, objectDetectionData)

    returnData = {
        "outerMostRedLight": None,
        "outerMostGreenLight": None,
        "signSpeed": None
    }

    if outerMostRedLight: returnData["outerMostRedLight"] = outerMostRedLight
    if outerMostRedLight: returnData["outerMostGreenLight"] = outerMostGreenLight
    if outerMostSign: returnData["signSpeed"] = outerMostSign

    return returnData

def steeringLogic(): # run in thread
    while True:
        esp32Data["steeringDegrees"] = 90

        if bool(cameraLineSteeringPercentage["links"]) and not bool(cameraLineSteeringPercentage["rechts"]):
            esp32Data["steeringDegrees"] = cameraLineSteeringPercentage["links"] * (steeringRange / 2) + (steeringRange / 2)

        if not bool(cameraLineSteeringPercentage["links"]) and bool(cameraLineSteeringPercentage["rechts"]):
            esp32Data["steeringDegrees"] = cameraLineSteeringPercentage["rechts"] * (steeringRange / 2)
        # print(esp32Data["steeringDegrees"])


def sendKartControlData(): # run in thread
    while True:
        esp32ParentPipe.send(esp32Data)
        time.sleep(0.005)

    
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

def getOuterMostColorLight(i, c, color):
    outerMostLight = None
    lights = []

    if objectDetectionData.names[int(c)] == color:  # Filter result based on class
        maxXCoord = objectDetectionData.boxes.xyxy[i][2]
        lights.append(maxXCoord)
        if outerMostLight is None:
            outerMostLight = maxXCoord
        if maxXCoord > outerMostLight: outerMostLight = maxXCoord
        print(lights)
        if outerMostLight is not None:
            print(outerMostLight)

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
    
def lowPassFilter(validClassNames, resultHistory, hitPercentage): 
    filteredSet = set()
    resultHistoryLength = len(resultHistory)
    for className in validClassNames:
        registeredObjectFrames = sum(className in historyFrame for historyFrame in resultHistory)
        if registeredObjectFrames / resultHistoryLength > hitPercentage:
            filteredSet.add(className)
    return filteredSet

# def gasControl():
#     while True:
#         while currentSpeed <= newSpeed:

def yoloStart():
    global easyOcrReader
    yolov8ParentPipe, yolov8ChildPipe = Pipe()
    yolov8Process = Process(target=ObjectDetection().detect, args=(yolov8ChildPipe,), daemon=True)
    yolov8DataThread = threading.Thread(target=getProcessData, args=(yolov8ParentPipe, "yolov8"), daemon=True)
    easyOcrReader = easyocr.Reader(['en'], gpu=False)
    yolov8Process.start()
    yolov8DataThread.start()

def esp32Start():
    global esp32ParentPipe
    esp32ParentPipe, esp32ChildPipe = Pipe()
    esp32Process = Process(target=ESP32().connect, args=(esp32ChildPipe,), daemon=True)
    esp32Process.start()

def lineDetectionStart():
    lineDetectionParentPipe, lineDetectionChildPipe = Pipe()
    lineDetectionProcess = Process(target=Detection().run, args=(lineDetectionChildPipe,), daemon=True)
    lineDetectionProcess.start()
    lineDetectionDataThread = threading.Thread(target=getProcessData, args=(lineDetectionParentPipe, "lineDetection"), daemon=True)
    lineDetectionDataThread.start()


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
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    defaultSpeed = 10
    desSpeed = 5
    steeringRange = 180
    easyOcrReader = None
    lineDetectionData = None
    objectDetectionData = None

    cameraLineSteeringPercentage = {
        "links": 0,
        "rechts": 0,
        "voor": 0
    }

    esp32Data = {
        "motorPWM": 0,
        "brakePWM": 0,
        "steeringAngle": 90
    }
    
    yoloStart()
    lineDetectionStart()

    while lineDetectionData is None:
        time.sleep(0.01)

    while objectDetectionData is None:
        time.sleep(0.01)

    while True:
        drivingAlgorithm()
