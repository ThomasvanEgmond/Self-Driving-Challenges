from ultralytics import YOLO            # pip install ultralytics
import numpy as np
import math
import cv2

model = YOLO('yolov8n_openvino_model/', task='detect')
camera = cv2.VideoCapture(0)
framecount = 0

def normalToSegment(n):
    return int(n*4)

# def xyxyToCenter(x0,y0,x1,y1):
#     return x0+(x1-x0)/2, y0+(y1-y0)/2

def personDetection(frame, saveFrame=False):
    results = model(frame, classes=[0], conf=0.5) # find persons in view
    # print(results)
    for result in results:
        if saveFrame: result.save("images/pedestrian_test_frame.png")
        print(result.boxes.cls)
        boxes = result.boxes.xyxyn.tolist()
        for box in boxes:
            segmentCenter = normalToSegment(box[0]+(box[2]-box[0])/2)
            for i in range(len(box)):
                print(round(box[i],2), end=",\t") # print normalised coördinates
            print(f"segment min-max: {normalToSegment(box[0])}-{normalToSegment(box[2])}, segment center: {segmentCenter} ")

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