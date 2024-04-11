import cv2
import easyocr
from ultralytics import YOLO

# ==== runnen als ov_model nog niet bestaat ====
# model = YOLO("runs/merged_model/best.pt")
# model.export(format='openvino')
# ==============================================

ov_model = YOLO('runs/merged_model/best_openvino_model/')

reader = easyocr.Reader(['en'], gpu=False)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # cv2.imshow('frame', frame)
    results = ov_model.predict(frame, show=True, verbose=False, imgsz=800)[0]

    outerMostSign = None

    for i, c in enumerate(results.boxes.cls):
        if results.names[int(c)] == "sign":             # Filter results based on class
            boxResult = results.boxes.xyxy[i]
            if outerMostSign is None:
                outerMostSign = boxResult
            if boxResult[2] > outerMostSign[2]:         # compare x_max
                outerMostSign = boxResult
            if outerMostSign is not None:
                # print(outerMostSign)
                x_min, y_min, x_max, y_max = outerMostSign
                roi = frame[int(y_min):int(y_max), int(x_min):int(x_max)]       # crop frame using bb cords
                ocr_results = reader.readtext(roi)
                for (bbox, text, prob) in ocr_results:
                    print(text)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
