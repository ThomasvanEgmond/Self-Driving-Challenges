from ESP import ESP32 
from YOLO.YOLOv8 import ObjectDetection
from lijndetection.lines import Detection
from multiprocessing import Process
import os

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    lineDetectionProcess = Process(target=Detection().run)
    esp32Process = Process(target=ESP32().connect)
    yolov8Process = Process(target=ObjectDetection().detect)

    esp32Process.start()
    yolov8Process.start()
    lineDetectionProcess.start()
