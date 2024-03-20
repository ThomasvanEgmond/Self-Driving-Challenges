import cv2 as cv
class Camera:
    def __init__(self, number, cap, base_value, keyboardInputs, lower_white=100) -> None:
        self.number=number
        self.cap=cv.VideoCapture(cap)
        self.base_value=base_value 
        self.keyboardInputs=keyboardInputs # string of 5 chars for controls
        self.lower_white=lower_white
        self.calibrationCountDown=0
