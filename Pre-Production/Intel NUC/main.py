# from ESP import ESP32 
from YOLO_easyOCR.YOLOv8 import ObjectDetection
from lineDetection.lines import Detection
from multiprocessing import Process, Pipe
import easyocr
import threading
import os
import time

defaultSpeed = 10
desSpeed = 5
maxSteeringAngle = 90

cameraLineSegments = [-1,-1,-1] # [voor,links,rechts] -1 if no line detected

def drivingAlgorithm():
    global esp32ParentPipe
    global esp32Data
    global lineDetectionData
    global objectDetectionData
    global defaultSpeed
    global speedSignSpeed
    global motorPWM
    global newSpeed
    global currentSpeed

    global defaultSpeed
    global desSpeed
    global maxSteeringAngle

    global cameraLineSegments

    # print(lineDetectionData)
    # print(objectDetectionData)

    # esp32Data["brakePWM"] = lineDetectionData["segment"]
    # esp32ParentPipe.send(esp32Data)

    # outerMostRedLight = None
    # outerMostSign = None
    # redLights = []

    # getProcessData(lineDetectionParentPipe, lineDetectionData)
    # lineDetectedInFront = False

    # Update line segments
    cameraList = ["voor","links","rechts"]
    index = cameraList.index(lineDetectionData["camera"])
    if lineDetectionData["lineDetected"]:
        cameraLineSegments[index] = lineDetectionData["segment"]
    else: cameraLineSegments[index] = -1
    # print(cameraLineSegments)

    # gas/brake logic
    tempObData = objectDetectionData
    for i, c in enumerate(objectDetectionData.boxes.cls):
        match objectDetectionData.names[int(c)]:
            case "Red":
                if getOuterMostRedLight(i, c):
                    currentSpeed = desSpeed
                    if (cameraLineSegments[0]!=-1):
                        # stop()
                        pass

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
    
    # steering logic
    steeringAngle = 0
    if not (cameraLineSegments[1]!=-1 and cameraLineSegments[2]!=-1):
        for i,segment in enumerate(cameraLineSegments[1:]): # left/right camera
            if segment == -1:
                continue 
            print(i)
            steeringPercentage = segment/20 
            steeringAngle = steeringPercentage * maxSteeringAngle
        if i == 0: steeringAngle = -steeringAngle # if line on left side: negatieve angle
    print(steeringAngle)

    # esp32Data["steeringDegrees"] = steeringAngle
    # esp32ParentPipe.send(esp32Data)
    

# def parseJSON():
#     getProcessData(lineDetectionParentPipe, lineDetectionData)
#     match lineDetectionData.camera.name:
#         case "links":



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
        # print(lineDetectionData)
        # print(objectDetectionData.boxes.cls)
        drivingAlgorithm()
