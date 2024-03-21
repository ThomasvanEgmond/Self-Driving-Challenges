import numpy as np
import cv2 as cv
import Camera as cam

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

def check_for_lines(c):
    ret, frame = c.cap.read()
    if not ret:
        print(f"Can't receive frame (stream end?) from camera {c.number}. Exiting ...")
        return False  # Indicates that frame reading was unsuccessful
    
    # Make the left half of the frame black
    height, width = frame.shape[:2]
    frame[:, 0:width//2] = 0  # Set all pixels on the left side to black
    
    white_spots = detect_white_spots(frame, c.lower_white)
    
    # Note: You may want to apply the black out effect after detecting white spots
    # depending on whether you need the detection to run on the whole frame or just the visible part.
    # If after, make sure to adjust the `white_spots` image in a similar way.
    
    cv.imshow('Live White Spot Detection', white_spots)

    current_value=np.sum(white_spots)
    if np.sum(white_spots) > 100000:
        print(c.lower_white,current_value,"White line detected",c.calibrationCountDown, c.base_value-current_value)
    
    if c.calibrationCountDown > 0:
        if c.base_value-current_value<-100 or c.base_value-current_value>100:
            c.lower_white=calibrateLowerWhite(c.calibrationCountDown, c.lower_white, c.base_value, current_value)
        c.calibrationCountDown-=1

def checkKeyboardInputs(cameraList):
    key = cv.waitKey(1)
    if key == ord('q'):
        return False
    for c in cameraList:
        if key == ord(c.keyboardInputs[0]) and c.lower_white < 255:
            c.lower_white += 1
        if key == ord(c.keyboardInputs[1]) and c.lower_white > 0:
            c.lower_white -= 1
        if key == ord(c.keyboardInputs[2]) and c.lower_white < 245:
            c.lower_white += 10
        if key == ord(c.keyboardInputs[3]) and c.lower_white > 10:
            c.lower_white -= 10
        if key == ord(c.keyboardInputs[4]): # calibrate
            c.calibrationCountDown = 7
            c.lower_white=127
    return True

def main():
    c1=cam.Camera(1,0,1138575,"edwsc")
    c2=cam.Camera(2,1,1138575,"ujikm")
    cameraList=[c1,c2]

    if not c1.cap.isOpened() or not c2.cap.isOpened():
        print("Cannot open one or both cameras")
        exit()
    
    while True:
        line_detected_cam1 = check_for_lines(c1)
        line_detected_cam2 = check_for_lines(c2)

        if not checkKeyboardInputs(cameraList):
            break


    c1.cap.release()
    c2.cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
