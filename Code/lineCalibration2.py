import numpy as np
import cv2 as cv
import Camera as cam

def black_white_processing(frame, lower_white):
    # Optimize the kernel size if possible or consider processing at a lower resolution
    kernel_size = 5  # Slightly smaller kernel might still serve your purpose
    blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    grayScaleFrame = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
    
    upper_white = 255
    blackWhiteFrame = cv.inRange(grayScaleFrame, lower_white, upper_white)  # filters only white

    return blackWhiteFrame

def calibrateLowerWhite(calibrationCountDown, lower_white, base_value, current_value):
    if current_value<base_value: return lower_white-2**(calibrationCountDown-1)
    return lower_white+2**(calibrationCountDown-1)

def check_for_lines(camera):
    line_detected = False
    ret, frame = camera.cap.read()
    if not ret:
        print(f"Can't receive frame (stream end?) from camera {camera.name}. Exiting ...")
        return False  # Indicates that frame reading was unsuccessful
    
    # Make the left half of the frame black
    # height, width = frame.shape[:2]
    # frame[:, 0:width//2] = 0  # Set all pixels on the left side to black
    
    blackWhiteFrame = black_white_processing(frame, camera.lower_white)

    # print("new ")
    # print(blackWhiteFrame)
    
    # Note: You may want to apply the black out effect after detecting white spots
    # depending on whether you need the detection to run on the whole frame or just the visible part.
    # If after, make sure to adjust the `white_spots` image in a similar way.
    
    cv.imshow('Live White Spot Detection '+ camera.name, blackWhiteFrame)

    white_pixels = np.sum(blackWhiteFrame) / 255
    if white_pixels > 1664:
        line_detected = True

    print("\n---------------------------------")
    print(f"Camera = {camera.name}\nLower_white = {camera.lower_white}\nWhite pixel = {white_pixels}\nWhite line detected = {line_detected}")
    print("---------------------------------")

    if camera.calibrationCountDown > 0:
        if camera.base_value-white_pixels<-100 or camera.base_value-white_pixels>100:
            camera.lower_white=calibrateLowerWhite(camera.calibrationCountDown, camera.lower_white, camera.base_value, white_pixels)
        camera.calibrationCountDown-=1

def checkKeyboardInputs(cameraList):
    key = cv.waitKey(1)
    if key == ord('q'):
        return False
    for camera in cameraList:
        if key == ord(camera.keyboardInputs[0]) and camera.lower_white < 255:
            camera.lower_white += 1
        if key == ord(camera.keyboardInputs[1]) and camera.lower_white > 0:
            camera.lower_white -= 1
        if key == ord(camera.keyboardInputs[2]) and camera.lower_white < 245:
            camera.lower_white += 10
        if key == ord(camera.keyboardInputs[3]) and camera.lower_white > 10:
            camera.lower_white -= 10
        if key == ord(camera.keyboardInputs[4]): # camera calibrate
            camera.calibrationCountDown = 7
            camera.lower_white=127
    return True

def main():
    cameraList=[]
    cameraList.append(cam.Camera("rechts",0,141439,"edwsc"))
    cameraList.append(cam.Camera("links",1,140516,"ujikm"))


    for camera in cameraList:
            if not camera.cap.isOpened():
                print("Cannot open camera nr."+ camera.name)
                exit()   
    
    while True:
        for camera in cameraList:
            check_for_lines(camera)

        if not checkKeyboardInputs(cameraList):
            break


    for camera in cameraList:
            camera.cap.release()

    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
