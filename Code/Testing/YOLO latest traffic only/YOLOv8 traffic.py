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

    def detect(self,):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # cv2.imshow('frame', frame)
            results = self.ov_model.predict(frame, show=True, verbose=False, imgsz=800)[0]

            outerMostRedLight = None
            redLights = []

            # print(type(results.names))
            # names = ov_model.names
            for i, c in enumerate(results.boxes.cls):
                match results.names[int(c)]:
                    case "Red":
                        if results.names[int(c)] == "Red":  # Filter results based on class
                            redLights.append(results.boxes.xyxy[i][2])
                            boxResult = results.boxes.xyxy[i][2]
                            if outerMostRedLight is None:
                                outerMostRedLight = results.boxes.xyxy[i][2]
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