import numpy as np
import cv2 as cv

def detect_white_spots(frame):
    # Blurr the image and then turn into greyscale
    kernel_size = 5
    blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    grey = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

    # Lower and upper bound for detecting white
    lower_white = 253  # Adjust this value to capture the white intensity you're interested in
    upper_white = 255
    white_spots = cv.inRange(grey, lower_white, upper_white)  # filters for the range of white

    return white_spots

def check_segments(white_spots):
    height = white_spots.shape[0]
    segment_height = height // 4
    for i in range(4):
        segment = white_spots[i * segment_height:(i + 1) * segment_height, :]
        if np.sum(segment) > 500:  # This threshold might need adjusting
            print(f"White spot detected in segment {i + 1}")

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
        
        # Detect white spots
        white_spots = detect_white_spots(frame)
        
        # Check segments for white spot detection
        check_segments(white_spots)
        
        # Display the resulting frame
        cv.imshow('White Spot Detection', white_spots)
        
        # Break the loop
        if cv.waitKey(1) == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
3