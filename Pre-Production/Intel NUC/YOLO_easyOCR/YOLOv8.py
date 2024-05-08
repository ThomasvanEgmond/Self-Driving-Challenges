import os
from ultralytics import YOLO
import cv2
import easyocr
from multiprocessing import Process
from queue import Queue

# ==== runnen als ov_model nog niet bestaat ====
# model = YOLO("runs/detect/train10/best.pt")
# model.export(format='openvino')
# ==============================================


class ObjectDetection:
    def __init__(self,):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.ov_model = YOLO('runs/merged_model/best_openvino_model/', task="detect")
        self.childPipe = None

    def detect(self, childPipe):
        self.childPipe = childPipe
        # ocrObject = charDetection()
        while True:
            results = self.ov_model(source="0", show=True, verbose=False, imgsz=800, stream=True)
            # queue = Queue(maxsize = 60)
            # for frame in qu
            for result in results:
                self.childPipe.send(result)
                # print(result.orig_img)

                # data ={
                #     "camara": camera.name,
                #     "lineDetected": line_detected,
                #     "segment": segmentNumber
                # }

                continue
                # outerMostRedLight = None
                # outerMostSign = None
                # redLights = []

                # for index, classID in enumerate(result.boxes.cls):
                #     match result.names[int(classID)]:
                #         case "Red":
                #             # if result.names[int(classID)] == "Red":  # Filter result based on class
                #             maxXCoord = result.boxes.xyxy[index][2]
                #             redLights.append(maxXCoord)
                #             if outerMostRedLight is None:
                #                 outerMostRedLight = maxXCoord
                #             if maxXCoord > outerMostRedLight: outerMostRedLight = maxXCoord
                #             print(redLights)
                #             if outerMostRedLight is not None: print(outerMostRedLight)
                #         case "Green":
                #             print("Green???")

                #         case "sign":
                #             signCoords = result.boxes.xyxy[index]
                #             if outerMostSign is None:
                #                 outerMostSign = signCoords
                #             if signCoords[2] > outerMostSign[2]:         # compare x_max
                #                 outerMostSign = signCoords

                #         case _:
                #             pass

                # if outerMostSign is not None:
                #     self.childPipe.send((result, ocrObject.detect(outerMostSign, result)))
                    
                # else: self.childPipe.send((result, None))

                # if cv2.waitKey(0) & 0xFF == ord('q'):
                #     break
                # print("end loop")

