from ESP import ESP32 
from YOLO_easyOCR.YOLOv8 import ObjectDetection
from lineDetection.lines import Detection
from multiprocessing import Process, Pipe
from Revolutions import Revolutions
import easyocr
import threading
import os
import time

def drivingAlgorithm():
    global desSpeed
    global waitingOnGreenLight
    global waitingOnPedestrian
    parsedData = parseObjectDetectionData()

    if waitingOnGreenLight and "Green" in parsedData and not "Red" in parsedData:
        desSpeed = signSpeed
        waitingOnGreenLight = False

    if waitingOnPedestrian:
        pass
        # startSegment = bla bla 1
        # if person not in startSegment and is in end segment:
        # waitingOnPedestrian = false 


    if not waitingOnPedestrian or not waitingOnGreenLight: desSpeed = signSpeed
    else: return

    if "Red" in parsedData:
        if not waitingOnGreenLight: desSpeed = 5
        if frontCameraSegment >= 2:
            desSpeed = 0
            waitingOnGreenLight = True

    if "Person" in parsedData:
        if not waitingOnPedestrian: desSpeed = 5
        if frontCameraSegment >= 1:
            desSpeed = 0
            waitingOnPedestrian = True

            

def steeringLogic(): # run in thread
    while True:
        esp32Data["steeringDegrees"] = 90

        if bool(leftCameraSteeringPercentage) and not bool(rightCameraSteeringPercentage):
            esp32Data["steeringDegrees"] = leftCameraSteeringPercentage * (steeringRange / 2) + (steeringRange / 2)

        if not bool(leftCameraSteeringPercentage) and bool(rightCameraSteeringPercentage):
            esp32Data["steeringDegrees"] = rightCameraSteeringPercentage * (steeringRange / 2)
        # print(esp32Data["steeringDegrees"])


def sendKartControlData(): # run in thread
    while True:
        esp32ParentPipe.send(esp32Data)
        time.sleep(0.005)

def ocrDetect(outerMostSign, result):
    x_min, y_min, x_max, y_max = outerMostSign
    roi = result.orig_img[int(y_min):int(y_max), int(x_min):int(x_max)]  # crop frame using bb cords
    for (bbox, text, prob) in easyOcrReader.readtext(roi):
        print(text)
        return text
    
def parseObjectDetectionData():
    global lastKnownObjectState
    global resultHistory
    global signSpeed

    outerMostRedLight = 0
    outerMostGreenLight = 0
    outerMostSign = 0

    lastKnownObjectState = {}   
    resultHistory = [] 
    resultHistorySize = 30

    tempObjectDetectionData = objectDetectionData
    detectedClassesSet = set()

    for i, c in enumerate(tempObjectDetectionData.boxes.cls):
        className = tempObjectDetectionData.names[int(c)]
        detectedClassesSet.add(className)
        coords = tempObjectDetectionData.boxes.xyxy[i]
        maxXCoord = coords[2]
        match className:
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

    if outerMostRedLight: lastKnownObjectState["Red"] = outerMostRedLight
    if outerMostGreenLight: lastKnownObjectState["Green"] = outerMostGreenLight
    if outerMostSign: lastKnownObjectState["Sign"] = outerMostSign

    if len(resultHistory) == resultHistorySize:
        resultHistory.pop(resultHistorySize - 1)
    resultHistory.insert(0, detectedClassesSet)

    
    filteredSet = lowPassFilter(tempObjectDetectionData.names.values(), resultHistory, 0.25)

    # gefilterde lijst met welke objecten we nu detecteren VVV
    # lijst met lastKnownObjectState["Red"] = boxes VVV

    returnData = {}
    for object in filteredSet:
        returnData[object] = lastKnownObjectState[object]

    return returnData
    
def lowPassFilter(validClassNames, resultHistory, hitPercentage):
    filteredSet = set()
    resultHistoryLength = len(resultHistory)
    for className in validClassNames:
        registeredObjectFrames = sum(className in historyFrame for historyFrame in resultHistory)
        if registeredObjectFrames / resultHistoryLength > hitPercentage:
            filteredSet.add(className)
    return filteredSet

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
    esp32Process.start()\
    
def revCounterStart():
    global revParentPipe
    revParentPipe, revChildPipe = Pipe()
    revProcess = Process(target=Revolutions().getRevolutions, args=(revChildPipe,), daemon=True)
    revProcess.start()

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
                    global leftCameraSteeringPercentage
                    global rightCameraSteeringPercentage
                    global frontCameraSegment
                    if data["camera"] == "voor": frontCameraSegment = data["segment"]
                    if data["camera"] == "links": leftCameraSteeringPercentage = data["steeringPercentage"]
                    if data["camera"] == "rechts": rightCameraSteeringPercentage = data["steeringPercentage"]

                case "yolov8":
                    global objectDetectionData
                    objectDetectionData = data
                case "revolutions":
                    global revs
                    revs  = data

def gasAndBrakeAlgorithm():
    global desSpeed
    global curSpeed
    motorPWM  = 0
    brakePWM = 0

    # curSpeed = berekening met revs
    # if des > curspeed bla bla curve

    #  bla bla bereken hoeveel brakePWM als nodig

    esp32Data["motorPWM"] = motorPWM
    if brakePWM: esp32Data["brakePWM"] = brakePWM

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    waitingOnPedestrian = False
    waitingOnGreenLight = False
    signSpeed = 10
    curSpeed = 0
    desSpeed = 10
    steeringRange = 180

    leftCameraSteeringPercentage = 0
    rightCameraSteeringPercentage = 0
    frontCameraSegment = 0

    esp32Data = {
        "motorPWM": 0,
        "brakePWM": 0,
        "steeringDegrees": 90
    }
    
    yoloStart()
    lineDetectionStart()

    while True:
        drivingAlgorithm()
