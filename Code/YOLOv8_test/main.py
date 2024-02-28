from ultralytics import YOLO            # pip install ultralytics
import cv2

model = YOLO("yolov8x.pt")              # model van yolov8 zelf
results = model.predict(source="0", show=True)
print(results)