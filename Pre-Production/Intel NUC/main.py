from ESP import ESP32 
from YOLO_easyOCR.YOLOv8 import ObjectDetection
from lineDetection.lines import Detection
from multiprocessing import Process, Pipe
from Revolutions import Revolutions
import easyocr
import threading
import os
import time

def drivingAlgorithm(parsedData):
    global desSpeed
    global waitingOnGreenLight
    global waitingOnPedestrian
    global personCrossingDone
    global personSegmentCount

    if waitingOnGreenLight and "Green" in parsedData and not "Red" in parsedData:
        print("Green light seen, driving")
        desSpeed = signSpeed
        waitingOnGreenLight = False

    if not waitingOnGreenLight: desSpeed = signSpeed
    else: 
        print("Waiting on green light")
        return

    if "Red" in parsedData:
        if not waitingOnGreenLight:
            print("Red light seen, driving slowly") 
            desSpeed = 5
        if frontCameraSegment >= 2:
            print("Red light and line seen, stopping")
            desSpeed = 0
            waitingOnGreenLight = True

    if "Person" in parsedData:
        global startSegment
        if not waitingOnPedestrian:
            startSegment = lastKnownObjectState["Person"]
            desSpeed = 5

        # stop crossing
        if waitingOnPedestrian and lastKnownObjectState["Person"] != startSegment and (lastKnownObjectState["Person"] == 1 or lastKnownObjectState["Person"] == personSegmentCount) :
            print("Person crossed, start driving")
            desSpeed = signSpeed
            waitingOnPedestrian = False
            personCrossingDone = True

        # start crossing
        if not waitingOnPedestrian and not personCrossingDone:
            if frontCameraSegment:
                desSpeed = 0
                waitingOnPedestrian = True
                startSegment = lastKnownObjectState["Person"]
                print(f"Person and crosswalk seen, stop driving, startSegment = {startSegment}")
            else: print("Person but no crosswalk seen")

        if personCrossingDone: print("Person seen but person crossing done, so driving")
    

    elif waitingOnPedestrian or personCrossingDone: resetCrossing() 

            

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
    global currentPersonSegment
    global personSegmentCount
    global objectDetectionData

    currentPersonSegment = 0
    outerMostRedLight = 0
    outerMostGreenLight = 0
    outerMostSign = 0
    personBox = [0, 0, 0, 0]

    detectedClassesSet = set()

    for i, c in enumerate(objectDetectionData.boxes.cls):
        className = objectDetectionData.names[int(c)]
        detectedClassesSet.add(className)
        coords = objectDetectionData.boxes.xyxy[i].tolist()
        normalizedCoords = objectDetectionData.boxes.xyxyn[i]
        maxXCoord = coords[2]
        match className:
            case "Red":
                if maxXCoord > outerMostRedLight: outerMostRedLight = maxXCoord

            case "Green":
                if maxXCoord > outerMostGreenLight: outerMostGreenLight = maxXCoord
            
            case "Sign":
                if not outerMostSign:
                    outerMostSign = coords
                if maxXCoord > outerMostSign[2]:         # compare x_max
                    outerMostSign = coords
            case "Person":
                if ((personBox[2]-personBox[0])*(personBox[3]-personBox[1]) < (normalizedCoords[2]-normalizedCoords[0])*(normalizedCoords[3]-normalizedCoords[1])):
                    personBox = normalizedCoords
                currentPersonSegment = normalToSegment(personSegmentCount, personBox[0]+(personBox[2]-personBox[0])/2)

    if outerMostSign != 0: signSpeed = ocrDetect(outerMostSign, objectDetectionData)

    if len(resultHistory) == resultHistorySize:
        resultHistory.pop(resultHistorySize - 1)
    resultHistory.insert(0, detectedClassesSet)

    
    filteredSet = lowPassFilter(objectDetectionData.names.values(), resultHistory, 0.5)

    if outerMostRedLight: lastKnownObjectState["Red"] = outerMostRedLight
    if outerMostGreenLight: lastKnownObjectState["Green"] = outerMostGreenLight
    if outerMostSign: lastKnownObjectState["Sign"] = outerMostSign
    if currentPersonSegment: lastKnownObjectState["Person"] = currentPersonSegment


    # gefilterde lijst met welke objecten we nu detecteren VVV
    # lijst met lastKnownObjectState["Red"] = boxes VVV

    returnData = {}
    for object in filteredSet:
        if object == "Yellow": continue
        returnData[object] = lastKnownObjectState[object]

    return returnData
    
def lowPassFilter(validClassNames, resultHistory, hitPercentage):
    filteredSet = set()
    resultHistoryLength = len(resultHistory)
    for className in validClassNames:
        registeredObjectFrames = sum(className in historyFrame for historyFrame in resultHistory)
        # if className == "Person": print(f'{registeredObjectFrames} / {resultHistoryLength} = {registeredObjectFrames / resultHistoryLength}')
        if registeredObjectFrames / resultHistoryLength > hitPercentage:
            filteredSet.add(className)
    return filteredSet

def normalToSegment(segmentCount, normalizedBoxCenter):
    return int(normalizedBoxCenter*segmentCount) + 1

def resetCrossing():
    global waitingOnPedestrian
    global personCrossingDone
    global startSegment
    global lastKnownObjectState
    waitingOnPedestrian = False # is true while a person is crossing
    personCrossingDone = False # is true after a person has crossed and resets when no person detected
    startSegment = -1 # segment where person is first detected
    # lastKnownObjectState["Person"] = -1 # current segment of person during crossing
    print("crossing reset")

def yoloStart():
    global objectDetectionData
    global easyOcrReader
    objectDetectionData = None
    yolov8ParentPipe, yolov8ChildPipe = Pipe()
    yolov8Process = Process(target=ObjectDetection().detect, args=(yolov8ChildPipe,), daemon=True)
    yolov8DataThread = threading.Thread(target=getProcessData, args=(yolov8ParentPipe, "yolov8"))
    easyOcrReader = easyocr.Reader(['en'], gpu=False)
    yolov8Process.start()
    yolov8DataThread.start()
    while objectDetectionData is None:
        pass

def esp32Start():
    global esp32ParentPipe
    esp32ParentPipe, esp32ChildPipe = Pipe()
    esp32Process = Process(target=ESP32().connect, args=(esp32ChildPipe,))
    esp32Process.start()\
    
def revCounterStart():
    global revParentPipe
    revParentPipe, revChildPipe = Pipe()
    revProcess = Process(target=Revolutions().getRevolutions, args=(revChildPipe,), daemon=True)
    revProcess.start()

def lineDetectionStart():
    global frontCameraSegment
    global leftCameraSteeringPercentage
    global rightCameraSteeringPercentage
    frontCameraSegment = 0
    leftCameraSteeringPercentage = 0
    rightCameraSteeringPercentage = 0
    lineDetectionParentPipe, lineDetectionChildPipe = Pipe()
    lineDetectionProcess = Process(target=Detection().run, args=(lineDetectionChildPipe,), daemon=True)
    lineDetectionProcess.start()
    lineDetectionDataThread = threading.Thread(target=getProcessData, args=(lineDetectionParentPipe, "lineDetection"))
    lineDetectionDataThread.start()
    while frontCameraSegment is None:
        pass

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
                    drivingAlgorithm(parseObjectDetectionData())
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

    lastKnownObjectState = {}
    waitingOnGreenLight = False
    signSpeed = 10
    curSpeed = 0
    desSpeed = 10
    steeringRange = 180
    resultHistory = [] 
    resultHistorySize = 60

    leftCameraSteeringPercentage = 0
    rightCameraSteeringPercentage = 0
    frontCameraSegment = 0

    waitingOnPedestrian = False # is true while a person is crossing
    personCrossingDone = False # is true after a person has crossed and resets when no person detected
    startSegment = -1 # segment where person is first detected
    currentSegment = -1 # current segment of person during crossing
    currentPersonSegment = -1
    personSegmentCount = 4

    esp32Data = {
        "motorPWM": 0,
        "brakePWM": 0,
        "steeringDegrees": 90
    }
    
    yoloStart()
    lineDetectionStart()
