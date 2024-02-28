import numpy as np
import cv2 as cv

def histogram_equalization(image):
    # Convert the image to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # Apply histogram equalization
    equalized = cv.equalizeHist(gray)
    # Convert the equalized image back to BGR
    equalized_bgr = cv.cvtColor(equalized, cv.COLOR_GRAY2BGR)
    return equalized_bgr

def detect_lines(frame):
    # Blurr the image and then turn it into greyscale
    kernel_size = 7
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
    return edges
 
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
        
        # Apply histogram equalization
        equalized_frame = histogram_equalization(frame)
        
        # Detect lines on the original frame
        edges_original = detect_lines(frame)
        
        # Detect lines on the equalized frame
        edges_equalized = detect_lines(equalized_frame)
        
        # Display the original frame with edge detection
        cv.imshow('Edge Detection on Original Frame', edges_original)
        
        # Display the equalized frame with edge detection
        cv.imshow('Edge Detection on Equalized Frame', edges_equalized)
        
        # Break the loop
        if cv.waitKey(1) == ord('q'):
            break
 
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()
 
if __name__ == "__main__":
    main()
