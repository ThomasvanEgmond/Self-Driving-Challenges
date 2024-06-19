from ultralytics import YOLO
import cv2

ov_model = YOLO('yolov8n_openvino_model/', task='detect')
camera = cv2.VideoCapture(0)
framecount = 0

filteredObjects = []		# objects after filtering
objectsCounter = [] 		# counts frames of objects before adding to filteredObjects, contains tuple of (object class, counter)

n = 10 # amount of frames before object counts as detected

def frameFilter(objectsCurrentFrame): # takes list object classes as input
    global filteredObjects
    global objectsCounter

    # add detected objects to objectsCounter
    objectsInCounter = {i[0] for i in objectsCounter}
    for object in set(objectsCurrentFrame):
        if object not in objectsInCounter:
            objectsCounter.append((object,0))

    for i,(object,counter) in enumerate(objectsCounter):
        # adjust counters
        if object in objectsCurrentFrame and counter < n: counter+=1
        if object not in objectsCurrentFrame and counter > 0: counter-=1

        # reset counters if amount of frames isn't reached
        if object in filteredObjects and object in objectsCurrentFrame: counter = n
        if object not in filteredObjects and object not in objectsCurrentFrame: counter = 0

        # update objects in filteredObjects and objectCounters
        objectsCounter[i] = (object,counter)
        if counter == n and object not in filteredObjects: filteredObjects.append(object)
        if counter == 0: 
            if object in filteredObjects: filteredObjects.remove(object)
            del objectsCounter[i]

    print(f"filtered objects: {filteredObjects},\t counters: {objectsCounter}")


while True:
    framecount+=1
    ret, frame = camera.read()

    if not ret:
        print("failed to grab frame")
        break
    
    k = cv2.waitKey(1)
    if k%256 == 27: # ESC pressed
        print("Escape hit, closing...")
        break

    results = ov_model.predict(frame, conf=0.5, verbose=False, show=True)
    
    # if framecount%10==0:
    for result in results:
        objects = result.boxes.cls.tolist()
        frameFilter(objects)

        boxes = result.boxes.xyxyn.tolist()
        filteredBoxes = [boxes[i] for i in range(len(objects)) if objects[i] in filteredObjects]
        # print(filteredBoxes)



camera.release()



        # filteredObjects = []

        # for i,object in enumerate(objectsCurrentFrame):
        #     currentObjectList = [i['object'] for i in objectsCounter]
        #     if object not in currentObjectList:
        #         objectsCounter.append({'object':object, 'frameCounter':0}) # add object to objectsCounter
        #     else:
        #         objectsCounter[i]['frameCounter'] +=1 # increment counter of object

        # for counter in objectsCounter:
        #     object,frameCounter=counter['object'],counter['frameCounter']
        #     if frameCounter >= 5 and object not in filteredObjects:
        #         filteredObjects.append(object) # add object to filteredObjects
        #         print(object,"added")
        #     if object not in objectsCurrentFrame and object not in [i['object'] for i in removeObjectsCounter]:
        #         # objectsCounter.remove(counter) # remove object from objectsCounter
        #         removeObjectsCounter.append({'object':object, 'frameCounter':0}) # remove object from objectsCounter

        # for i,counter in enumerate(removeObjectsCounter):
        #     removeObjectsCounter[i]['frameCounter'] +=1
        #     object,frameCounter=counter['object'],counter['frameCounter']
        #     if frameCounter >= 5:
        #         filteredObjects.remove(object) # remove object to filteredObjects
        #         removeObjectsCounter.remove(counter) # remove object from removeObjectsCounter
        #         objectsCounter.remove(counter) # remove object from objectsCounter
        #         print(object,"removed")
        #     if object in objectsCurrentFrame:
        #         removeObjectsCounter.remove(counter) # remove object from removeObjectsCounter