import os
from ultralytics import YOLO
import cv2
from queue import Queue

# ==== runnen als ov_model nog niet bestaat ====
# model = YOLO("runs/detect/train10/best.pt")
# model.export(format='openvino')
# ==============================================



class ObjectDetection:
    def __init__(self,):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.ov_model = YOLO('runs/detect/train10/best_openvino_model/')
        # self.filteredObjects = []		# objects after filtering
        # self.objectsCounter = [] 		# counts frames of objects before adding to filteredObjects, contains tuple of (object class, counter)

        # self.filteredFrames = 10 # amount of frames before object counts as detected

    def lowPassFilter(self, names, unfilteredList, hitPercentage):
        filteredSet = set()
        unfilteredListLength = len(unfilteredList)
        for className in names:
            registeredObjectFrames = sum(className in historyFrame for historyFrame in unfilteredList)
            # print(className, registeredObjectFrames)
            
            if registeredObjectFrames / unfilteredListLength > hitPercentage:
                filteredSet.add(className)
        return filteredSet

  
    def detect(self,):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # cv2.imshow('frame', frame)
            # results = self.ov_model.predict(frame, show=True, verbose=False, imgsz=800)
            results = self.ov_model(source="0", show=True, verbose=False, imgsz=800, stream=True)

            # print(type(results.names))
            # names = ov_model.names

            # print(results.boxes.cls.tolist())
            resultHistory = []
            setHistory = []
            for result in results:
                # self.result = result
                outerMostRedLight = None
                redLights = []
                classesSet = set()

                for i, c in enumerate(result.boxes.cls):
                    classesSet.add(result.names[int(c)])
                    match result.names[int(c)]:
                        case "Red":
                            if result.names[int(c)] == "Red":  # Filter results based on class
                                boxResult = result.boxes.xyxy.tolist()[i][2]
                                redLights.append(boxResult)
                                if outerMostRedLight is None:
                                    outerMostRedLight = boxResult
                                if boxResult > outerMostRedLight: outerMostRedLight = boxResult
                                # print(redLights)
                                # if outerMostRedLight is not None: print(outerMostRedLight)
                        # case "Green":
                        #     print("Green???")

                        case _:
                            pass
                    # print(results.names[int(c)])

                resultHistorySize = 20
                setHistorySize = 20
                if len(resultHistory) == resultHistorySize:
                    resultHistory.pop(resultHistorySize-1)
                resultHistory.insert(0, classesSet)
                # resultHistoryLength = len(resultHistory)
                
                
                # print(set(result.names.values()))
                if len(resultHistory) == resultHistorySize:
                    resultFiltered = self.lowPassFilter(result.names.values(), resultHistory, 0.25)
                    # print(resultFiltered)
                    if len(setHistory) == setHistorySize:
                        setHistory.pop(setHistorySize-1)
                    setHistory.insert(0, resultFiltered)
                    
                    # print(len(filteredObjects))
                    setFiltered = self.lowPassFilter(result.names.values(), setHistory, 0.25)
                    print(setFiltered)

                # filteredObjects = set()
                # for className in result.names.values():
                #         registeredObjectFrames = sum(className in historyFrame for historyFrame in resultHistory)
                #         # print(className, registeredObjectFrames)
                        
                #         if registeredObjectFrames / resultHistoryLength > 0.25 and resultHistoryLength / 60 > 0.75:
                #             filteredObjects.add(className)

                    # for result in resultHistory:
                



                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break

        self.cap.release()
        cv2.destroyAllWindows()


ObjectDetection().detect()