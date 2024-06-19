import cv2

def histogram_equalization(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply histogram equalization
    equalized = cv2.equalizeHist(gray)
    # Convert the equalized image back to BGR (for displaying)
    equalized_bgr = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
    return equalized_bgr

def main():
    # Open the default camera
    cap = cv2.VideoCapture(0)
 
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break
        # Apply histogram equalization
        equalized_frame = histogram_equalization(frame)
        # Display the original and equalized frames
        cv2.imshow('Original', frame)
        cv2.imshow('Equalized', equalized_frame)
        # Break the loop
        if cv2.waitKey(1) == ord('q'):
            break
 
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
