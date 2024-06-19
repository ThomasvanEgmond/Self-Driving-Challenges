import os
from ultralytics import YOLO
import cv2

# ==== runnen als ov_model nog niet bestaat ====
# model = YOLO("runs/detect/train10/best.pt")
# model.export(format='openvino')
# ==============================================



class ObjectDetection:
    def __init__(self,):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.ov_model = YOLO('runs/detect/train10/best_openvino_model/')
        self.filteredObjects = []		# objects after filtering
        self.objectsCounter = [] 		# counts frames of objects before adding to filteredObjects, contains tuple of (object class, counter)

        self.filteredFrames = 10 # amount of frames before object counts as detected

    def frameFilter(self, objectsCurrentFrame): # takes list object classes as input
        # global filteredObjects
        # global objectsCounter
        # global filteredFrames

        # add detected objects to objectsCounter
        objectsInCounter = {i[0] for i in self.objectsCounter}
        for object in set(objectsCurrentFrame):
            if object not in objectsInCounter:
                self.objectsCounter.append((object,0))

        for i,(object,counter) in enumerate(self.objectsCounter):
            # adjust counters
            if object in objectsCurrentFrame and counter < self.filteredFrames: counter+=1
            if object not in objectsCurrentFrame and counter > 0: counter-=1

            # reset counters if amount of frames isn't reached
            if object in self.filteredObjects and object in objectsCurrentFrame: counter = self.filteredFrames
            if object not in self.filteredObjects and object not in objectsCurrentFrame: counter = 0

            # update objects in filteredObjects and objectCounters
            self.objectsCounter[i] = (object,counter)
            if counter == self.filteredFrames and object not in self.filteredObjects: self.filteredObjects.append(object)
            if counter == 0: 
                if object in self.filteredObjects: self.filteredObjects.remove(object)
                del self.objectsCounter[i]

        print(f"filtered objects: {self.filteredObjects},\t counters: {self.objectsCounter}")


    def detect(self,):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # cv2.imshow('frame', frame)
            result = self.ov_model.predict(frame, show=True, verbose=False, imgsz=800)[0]

            objects = result.boxes.cls.tolist()
            self.frameFilter(objects)

            boxes = result.boxes.cls.tolist()
            filteredBoxes = [boxes[i] for i in range(len(objects)) if objects[i] in self.filteredObjects]

            outerMostRedLight = None
            redLights = []

            # print(type(results.names))
            # names = ov_model.names

            # print(results.boxes.cls.tolist())
            for i, c in enumerate(filteredBoxes):
                match result.names[int(c)]:
                    case "Red":
                        if result.names[int(c)] == "Red":  # Filter results based on class
                            boxResult = result.boxes.xyxy.tolist()[i][2]
                            redLights.append(boxResult)
                            if outerMostRedLight is None:
                                outerMostRedLight = boxResult
                            if boxResult > outerMostRedLight: outerMostRedLight = boxResult
                            print(redLights)
                            if outerMostRedLight is not None: print(outerMostRedLight)
                    case "Green":
                        print("Green???")

                    case _:
                        pass
                # print(results.names[int(c)])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


ObjectDetection().detect()