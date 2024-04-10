import numpy as np
import cv2 as cv

def detect_lines(frame):
    kernel_size = 7
    blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    grey = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

    lower_white = 240
    upper_white = 255
    white = cv.inRange(grey, lower_white, upper_white)

    low_threshold = 50
    high_threshold = 400
    edges = cv.Canny(white, low_threshold, high_threshold)
    return edges

def check_for_lines(cap, camera_number):
    ret, frame = cap.read()
    if not ret:
        print(f"Can't receive frame (stream end?) from camera {camera_number}. Exiting ...")
        return False  # Indicates that frame reading was unsuccessful
    
    edges = detect_lines(frame)
    cv.imshow(f'Live Edge Detection - Camera {camera_number}', edges)
    
    if np.sum(edges) > 500:
        print(f"Line detected on Camera {camera_number}")
        return True  # Indicates line detection

    return False  # Indicates no line detected

def main():
    cap1 = cv.VideoCapture(0)  # First webcam
    cap2 = cv.VideoCapture(1)  # Second webcam

    if not cap1.isOpened() or not cap2.isOpened():
        print("Cannot open one or both cameras")
        exit()

    while True:
        line_detected_cam1 = check_for_lines(cap1, 1)
        line_detected_cam2 = check_for_lines(cap2, 2)

        # If you want to perform a specific action when either camera detects a line,
        # you can do so by checking line_detected_cam1 or line_detected_cam2 here
        
        if cv.waitKey(1) == ord('q'):
            break

    cap1.release()
    cap2.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
