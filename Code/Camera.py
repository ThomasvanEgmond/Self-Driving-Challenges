import cv2 as cv
class Camera:
    def __init__(self, name, cap, base_value, type, keyboardInputs, lower_white=100) -> None:
        self.name=name
        self.cap=cv.VideoCapture(cap, cv.CAP_DSHOW)
        self.base_value=base_value 
        self.type=type
        self.keyboardInputs=keyboardInputs # string of 5 chars for controls
        self.lower_white=lower_white
        self.calibrationCountDown=0
