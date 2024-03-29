import numpy as np
import cv2 as cv
 
def detect_lines(frame, kernel_size):
    # Blurr the image and then turn into greyscale
    # kernel_size = 7
    blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    grey = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
 
    # Lower and upper bound for detecting white
    lower_white = 190
    upper_white = 255
    white = cv.inRange(grey, lower_white, upper_white)  # filters only white
 
    # Process edge detection, use Canny
    low_threshold = 50
    high_threshold = 400
    edges = cv.Canny(white, low_threshold, high_threshold)
    return white
 
def main():
    # Open the default camera
    cap = cv.VideoCapture(0)
 
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # frame = frame[0:1920,0:200]
        # Detect lines
        edges = detect_lines(frame,7)
        # Display the resulting frame
        cv.imshow('Live Camera', frame)
        cv.imshow('Live Camera cropped', frame[0:640,0:720])
        cv.imshow('Live Camera cropped2', frame[0:1280,0:360])
        # cv.imshow('Live Edge Detection7', edges)
        # cv.imshow('Live Edge Detection20', detect_lines(frame,21))
        # cv.imshow('Live Edge Detection30', detect_lines(frame,31))
        # Break the loop
        if cv.waitKey(1) == ord('q'):
            break
 
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()
 
if __name__ == "__main__":
    main()