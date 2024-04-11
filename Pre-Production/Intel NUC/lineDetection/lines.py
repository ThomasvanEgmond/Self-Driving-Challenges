import numpy as np
import cv2 as cv

class Detection:
    def __init__(self):
        self.whitePixelHitThreshold = 1664
        self.whitePixelSegmentHitThreshold = 416
        self.cameraList=[]

    def run(self):
        self.cameraList.append(Camera("voor",0,141439,"rftgb"))
        # self.cameraList.append(Camera("links",1,140516,"ujikm"))
        # self.cameraList.append(Camera("rechts",2,140516,"edwsc"))

        for camera in self.cameraList:
                if not camera.cap.isOpened():
                    print("Cannot open camera nr."+ camera.name)
                    exit()   
        
        while True:
            for camera in self.cameraList:
                self.check_for_lines(camera)

            if not self.checkKeyboardInputs(self.cameraList):
                break


        for camera in self.cameraList:
                camera.cap.release()

        cv.destroyAllWindows()

    def black_white_processing(self, frame, lower_white):
        # Optimize the kernel size if possible or consider processing at a lower resolution
        kernel_size = 5  # Slightly smaller kernel might still serve your purpose
        blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        grayScaleFrame = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
        
        upper_white = 255
        blackWhiteFrame = cv.inRange(grayScaleFrame, lower_white, upper_white)  # filters only white

        return blackWhiteFrame

    def calibrateLowerWhite(self, calibrationCountDown, lower_white, base_value, current_value):
        if current_value<base_value: return lower_white-2**(calibrationCountDown-1)
        return lower_white+2**(calibrationCountDown-1)

    # def check_segments4(self, blackWhiteFrame):
    #     height = blackWhiteFrame.shape[0]
    #     segment_height = height // 4
    #     for i in reversed(range(4)):
    #         segment = blackWhiteFrame[i * segment_height:(i + 1) * segment_height, :]
    #         white_pixels = np.sum(segment) / 255
    #         if white_pixels > 416:
    #             return i+1
            
    # def check_segments20(self, blackWhiteFrame):
    #     height = blackWhiteFrame.shape[0]
    #     segment_height = height // 20
    #     for i in reversed(range(20)):
    #         segment = blackWhiteFrame[i * segment_height:(i + 1) * segment_height, :]
    #         white_pixels = np.sum(segment) / 255
    #         if white_pixels > 416:
    #             return i+1
            
    def check_segments(self, blackWhiteFrame, segmentCount):
        height = blackWhiteFrame.shape[0]
        segment_height = height // segmentCount
        for i in reversed(range(segmentCount)):
            segment = blackWhiteFrame[i * segment_height:(i + 1) * segment_height, :]
            white_pixels = np.sum(segment) / 255
            if white_pixels > self.whitePixelSegmentHitThreshold:
                return i+1

    def check_for_lines(self, camera):
        line_detected = False
        ret, frame = camera.cap.read()
        if not ret:
            print(f"Can't receive frame (stream end?) from camera {camera.name}. Exiting ...")
            return False  # Indicates that frame reading was unsuccessful
        
        # Make the left half of the frame black
        # height, width = frame.shape[:2]
        # frame[:, 0:width//2] = 0  # Set all pixels on the left side to black
        
        blackWhiteFrame = self.black_white_processing(frame, camera.lower_white)

        # print("new ")
        # print(blackWhiteFrame)
        
        # Note: You may want to apply the black out effect after detecting white spots
        # depending on whether you need the detection to run on the whole frame or just the visible part.
        # If after, make sure to adjust the `white_spots` image in a similar way.
        
        
        # cv.imshow('camera',frame)
        cv.imshow(camera.name, blackWhiteFrame)

        white_pixels = np.sum(blackWhiteFrame) / 255
        # cv.setWindowTitle(camera.name, f"{camera.name}: Lower_white = {camera.lower_white}, White line detected = {line_detected}")
        cv.setWindowTitle(camera.name, f"{camera.name}: White line detected = {line_detected}")
        segmentNumberVoor = segmentNumberLinks = segmentNumberRechts = 0
        segmentNumber = 0
        if white_pixels > self.whitePixelHitThreshold:
            line_detected = True
            if camera.name == "voor":
                segmentNumber=self.check_segments(blackWhiteFrame, 4)
            else: # camera links/rechts
                segmentNumber=self.check_segments(blackWhiteFrame, 20)
            # cv.setWindowTitle(camera.name, f"{camera.name}: Lower_white = {camera.lower_white}, White line detected = {line_detected}, In segment {camera.name} = {segmentNumber}")
            cv.setWindowTitle(camera.name, f"{camera.name}: White line detected = {line_detected}, In segment {camera.name} = {segmentNumber}")
            print("\n---------------------------------")
            print(f"Camera = {camera.name}\nLower_white = {camera.lower_white}\nWhite pixel = {white_pixels}\nWhite line detected = {line_detected}\nIn segment {camera.name} = {segmentNumber}")
            print("---------------------------------")

            # if camera.name == "voor":
            #     segmentNumberVoor=self.check_segments4(blackWhiteFrame)
            #     print("\n---------------------------------")
            #     print(f"Camera = {camera.name}\nLower_white = {camera.lower_white}\nWhite pixel = {white_pixels}\nWhite line detected = {line_detected}\nIn segment Voor = {segmentNumberVoor}")
            #     print("---------------------------------")
            # if camera.name == "links":
            #     segmentNumberLinks=self.check_segments20(blackWhiteFrame)
            #     print("\n---------------------------------")
            #     print(f"Camera = {camera.name}\nLower_white = {camera.lower_white}\nWhite pixel = {white_pixels}\nWhite line detected = {line_detected}\nIn segment Links = {segmentNumberLinks}")
            #     print("---------------------------------")
            # if camera.name == "rechts":
            #     segmentNumberRechts=self.check_segments20(blackWhiteFrame)
            #     print("\n---------------------------------")
            #     print(f"Camera = {camera.name}\nLower_white = {camera.lower_white}\nWhite pixel = {white_pixels}\nWhite line detected = {line_detected}\nIn segment rechts = {segmentNumberRechts}")
            #     print("---------------------------------")

        if camera.calibrationCountDown > 0:
            if camera.base_value-white_pixels<-100 or camera.base_value-white_pixels>100:
                camera.lower_white=self.calibrateLowerWhite(camera.calibrationCountDown, camera.lower_white, camera.base_value, white_pixels)
            camera.calibrationCountDown-=1


    def checkKeyboardInputs(self, cameraList):
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

    # def main(self,):
    #     cameraList=[]
    #     cameraList.append(Camera("voor",0,141439,"rftgb"))
    #     cameraList.append(Camera("links",1,140516,"ujikm"))
    #     cameraList.append(Camera("rechts",2,140516,"edwsc"))


    #     for camera in cameraList:
    #             if not camera.cap.isOpened():
    #                 print("Cannot open camera nr."+ camera.name)
    #                 exit()   
        
    #     while True:
    #         for camera in cameraList:
    #             self.check_for_lines(camera)

    #         if not self.checkKeyboardInputs(cameraList):
    #             break


    #     for camera in cameraList:
    #             camera.cap.release()

    #     cv.destroyAllWindows()

    # if __name__ == "__main__":
    #     main()

class Camera:
    def __init__(self, name, cap, base_value, keyboardInputs, lower_white=100) -> None:
        self.name=name
        self.cap=cv.VideoCapture(cap, cv.CAP_DSHOW)
        self.base_value=base_value 
        self.keyboardInputs=keyboardInputs # string of 5 chars for controls
        self.lower_white=lower_white
        self.calibrationCountDown=0