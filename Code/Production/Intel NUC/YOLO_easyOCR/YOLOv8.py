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
        self.ov_model = YOLO('final_V5/best_openvino_model/', task="detect")
        self.child_pipe = None

    def detect(self, child_pipe):
        self.child_pipe = child_pipe
        while True:
            results = self.ov_model(source="0", show=True, verbose=False, imgsz=800, stream=True)

            for result in results:
                self.child_pipe.send(result)
                continue


