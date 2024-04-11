import os
from ultralytics import YOLO
import cv2
import easyocr
from multiprocessing import Process

# ==== runnen als ov_model nog niet bestaat ====
# model = YOLO("runs/detect/train10/best.pt")
# model.export(format='openvino')
# ==============================================


class charDetection:
    def __init__(self,):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def detect(self, outerMostSign, result):
        x_min, y_min, x_max, y_max = outerMostSign
        roi = result.orig_img[int(y_min):int(y_max), int(x_min):int(x_max)]  # crop frame using bb cords
        for (bbox, text, prob) in self.reader.readtext(roi):
            print(text)


class ObjectDetection:
    def __init__(self,):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.ov_model = YOLO('runs/merged_model/best_openvino_model/', task="detect")

    def detect(self,):
        ocrObject = charDetection()
        while True:
            results = self.ov_model(source="0", show=True, verbose=False, imgsz=800, stream=True)
            for result in results:
                # print(result.orig_img)

                outerMostRedLight = None
                outerMostSign = None
                redLights = []

                for i, c in enumerate(result.boxes.cls):
                    match result.names[int(c)]:
                        case "Red":
                            if result.names[int(c)] == "Red":  # Filter result based on class
                                maxXCoord = result.boxes.xyxy[i][2]
                                redLights.append(maxXCoord)
                                if outerMostRedLight is None:
                                    outerMostRedLight = maxXCoord
                                if maxXCoord > outerMostRedLight: outerMostRedLight = maxXCoord
                                print(redLights)
                                if outerMostRedLight is not None: print(outerMostRedLight)
                        case "Green":
                            print("Green???")

                        case "sign":
                            signCoords = result.boxes.xyxy[i]
                            if outerMostSign is None:
                                outerMostSign = signCoords
                            if signCoords[2] > outerMostSign[2]:         # compare x_max
                                outerMostSign = signCoords

                        case _:
                            pass

                if outerMostSign is not None:
                    print(outerMostSign)
                    ocrObject.detect(outerMostSign, result)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

