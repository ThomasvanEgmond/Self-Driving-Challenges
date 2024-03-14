import numpy as np
import cv2 as cv

def detect_white_spots(frame, lower_white):
    # Optimize the kernel size if possible or consider processing at a lower resolution
    kernel_size = 5  # Slightly smaller kernel might still serve your purpose
    blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    grey = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    
    upper_white = 255
    white_spots = cv.inRange(grey, lower_white, upper_white)  # filters only white

    return white_spots

def main():
    cap = cv.VideoCapture(0)
    lower_white = 100

    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # Make the left half of the frame black
        height, width = frame.shape[:2]
        frame[:, 0:width//2] = 0  # Set all pixels on the left side to black
        
        white_spots = detect_white_spots(frame, lower_white)
        
        # Note: You may want to apply the black out effect after detecting white spots
        # depending on whether you need the detection to run on the whole frame or just the visible part.
        # If after, make sure to adjust the `white_spots` image in a similar way.
        
        cv.imshow('Live White Spot Detection', white_spots)

        if np.sum(white_spots) > 100000:
            print("White line detected")
        
        key = cv.waitKey(1)
        
        if key == ord('q'):
            break
        if key == ord('d') and lower_white < 255:
            lower_white += 1
        if key == ord('u') and lower_white > 0:
            lower_white -= 1

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
