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

def calibrateLowerWhite(calibrationCountDown, lower_white, base_value, current_value):
    if current_value<base_value: return lower_white-2**(calibrationCountDown-1)
    return lower_white+2**(calibrationCountDown-1)

def main():
    cap = cv.VideoCapture(0)
    lower_white = 100
    base_value = 1138575 # road3.jpg, base value 1138575, lower_white 217
    calibrationCountDown = 0

    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    
    while True:
        frame = cv.imread("road3.jpg")
        # ret, frame = cap.read()
        
        # if not ret:
        #     print("Can't receive frame (stream end?). Exiting ...")
        #     break

        # Make the left half of the frame black
        # height, width = frame.shape[:2]
        # frame[:, 0:width//2] = 0  # Set all pixels on the left side to black
        
        white_spots = detect_white_spots(frame, lower_white)
        
        # Note: You may want to apply the black out effect after detecting white spots
        # depending on whether you need the detection to run on the whole frame or just the visible part.
        # If after, make sure to adjust the `white_spots` image in a similar way.
        
        cv.imshow('Live White Spot Detection', white_spots)

        current_value=np.sum(white_spots)
        if np.sum(white_spots) > 100000:
            print(lower_white,current_value,"White line detected",calibrationCountDown, base_value-current_value)
        
        if calibrationCountDown > 0:
            if base_value-current_value<-100 or base_value-current_value>100:
                lower_white=calibrateLowerWhite(calibrationCountDown, lower_white, base_value, current_value)
            calibrationCountDown-=1

        key = cv.waitKey(1)
        
        if key == ord('q'):
            break
        if key == ord('d') and lower_white < 255:
            lower_white += 1
        if key == ord('u') and lower_white > 0:
            lower_white -= 1
        if key == ord('w') and lower_white < 245:
            lower_white += 10
        if key == ord('s') and lower_white > 10:
            lower_white -= 10
        if key == ord('c'): # calibrate
            calibrationCountDown = 7
            lower_white=127

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
