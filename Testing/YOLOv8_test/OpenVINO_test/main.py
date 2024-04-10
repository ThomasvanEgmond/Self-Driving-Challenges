from ultralytics import YOLO            # pip install ultralytics

model = YOLO("yolov8n.pt")              # model van yolov8 zelf

model.export(format='openvino')

# Load the exported OpenVINO model
ov_model = YOLO('yolov8n_openvino_model/')

results = ov_model.predict(source="0", show=True)
# print(results)
