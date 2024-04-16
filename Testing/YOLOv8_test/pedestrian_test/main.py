from ultralytics import YOLO            # pip install ultralytics
import numpy as np
import math
import cv2

# ==== runnen als ov_model nog niet bestaat ====
# model = YOLO("yolov8n.pt")
# model.export(format='openvino')
# ==============================================

ov_model = YOLO('yolov8n_openvino_model/', task='detect')
camera = cv2.VideoCapture(0)
framecount = 0

personCrossing = False # is true while a person is crossing
personCrossingDone = False # is true after a person has crossed and resets when no person detected
startSegment = -1 # segment where person is first detected
currentSegment = -1 # current segment of person during crossing

segmentCount = 4

def normalToSegment(n):
    return int(n*segmentCount)

def personDetection(frame, saveFrame=False):
    results = ov_model.predict(frame, classes=[0], conf=0.5, verbose=False) # find persons in view
    # print(results)
    for result in results:
        if saveFrame: result.save("images/pedestrian_test_frame.png")
        # print(result.boxes.cls)
        boxes = result.boxes.xyxyn.tolist()
        print(f"{len(boxes)} person detected")
        # print(boxes)

        global personCrossing
        global personCrossingDone
        global startSegment

        # get person box
        personBox = []
        if len(boxes) == 0: 
            if personCrossingDone: 
                print("crossing reset")
                personCrossingDone = False
            break
        if len(boxes) == 1: personBox = boxes[0] 
        if len(boxes) > 1: # find largest person box 
            largestSize = 0
            largestBoxIndex = 0
            for i,box in enumerate(boxes):
                boxSize = (box[2]-box[0])*(box[3]-box[1])
                print(f"\tbox {i}: size = {boxSize}")
                if boxSize > largestSize: 
                    largestSize = boxSize
                    largestBoxIndex = i
            print(f"largest box is box {largestBoxIndex}")
            personBox = boxes[largestBoxIndex]

        # find segment 
        segmentCenter = normalToSegment(personBox[0]+(personBox[2]-personBox[0])/2)
        boxSize = (personBox[2]-personBox[0])*(personBox[3]-personBox[1])
        for i in personBox:
            print(f"\t{round(i,2)},", end="") # print normalised coördinates
        print(f"\tsize: {round(boxSize,2)},\tsegment min-max: {normalToSegment(personBox[0])}-{normalToSegment(personBox[2])}, segment center: {segmentCenter} ")
        currentSegment = segmentCenter
        # print(f"\tcurrentSegment = {currentSegment}")

        # start crossing
        if not personCrossing and not personCrossingDone:
            startSegment = currentSegment
            print(f"stop driving, startSegment = {startSegment}")
            personCrossing = True

        # stop crossing
        elif personCrossing and currentSegment != startSegment and (currentSegment == 0 or currentSegment == segmentCount-1) :
            print("start driving")
            personCrossing = False
            personCrossingDone = True
        


# personDetection(cv2.imread("images/Afbeelding5.png"), True)

while True:
    framecount+=1
    ret, frame = camera.read()

    if not ret:
        print("failed to grab frame")
        break
    
    cv2.imshow("test", frame)

    if framecount%50==0:
        personDetection(frame)

    k = cv2.waitKey(1)
    if k%256 == 27: # ESC pressed
        print("Escape hit, closing...")
        break
        
camera.release()