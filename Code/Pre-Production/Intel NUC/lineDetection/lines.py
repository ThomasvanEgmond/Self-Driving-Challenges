import numpy as np
import cv2 as cv

class Detection:
    def __init__(self):
        self.white_pixel_detection_threshold = 1664
        self.camera_list=[]
        self.child_pipe = None

    def run(self, child_pipe):
        self.child_pipe = child_pipe
        self.running = True

        # for each camera, first manually determine the white_pixel_calibration_value
        # self.camera_list.append(Camera("voor",1,141439, 4,'t', 'g', 'y', 'h', 'b'))
        self.camera_list.append(Camera("links",1,140516, 20,'e', 'd', 'r', 'f', 'c'))
        # self.camera_list.append(Camera("rechts",2,140516, 20,'u', 'j', 'i', 'k', 'm'))

        for camera in self.camera_list:
                if not camera.cap.isOpened():
                    print("Cannot open camera nr."+ camera.name)
                    exit()   
        
        while self.running:
            for camera in self.camera_list:
                self.check_for_lines(camera)
                self.handle_keyboard_input(camera)


        for camera in self.camera_list:
                camera.cap.release()

        cv.destroyAllWindows()

    def black_white_processing(self, frame, grayscale_split_value):
        # Optimize the kernel size if possible or consider processing at a lower resolution
        kernel_size = 5  # Slightly smaller kernel might still serve your purpose
        blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
        gray_scale_frame = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
        
        black_white_frame = cv.inRange(gray_scale_frame, grayscale_split_value, 255)  # filters only white

        return black_white_frame

    def calibrate_grayscale_split_value(self, remaining_calibration_frame_buffer, grayscale_split_value, white_pixel_calibration_value, current_value):
        if current_value<white_pixel_calibration_value:
            return grayscale_split_value-2**(remaining_calibration_frame_buffer-1)
        return grayscale_split_value+2**(remaining_calibration_frame_buffer-1)
            
    def check_segments(self, black_white_frame, amount_of_segments):
        segment_height = black_white_frame.shape[0] // amount_of_segments
        for segment_count in reversed(range(amount_of_segments)):
            segment_frame = black_white_frame[segment_count * segment_height:(segment_count + 1) * segment_height, :]
            white_pixels = np.sum(segment_frame) / 255
            if white_pixels > self.white_pixel_detection_threshold / amount_of_segments:
                return segment_count+1
        return 0

    def check_for_lines(self, camera):
        read_correctly, frame = camera.cap.read()
        if not read_correctly:
            print(f"Can't receive frame (stream end?) from camera {camera.name}. Exiting ...")
            return False  # Indicates that frame reading was unsuccessful
        
        # Make the left half of the frame black
        # height, width = frame.shape[:2]
        # frame[:, 0:width//2] = 0  # Set all pixels on the left side to black
        
        black_white_frame = self.black_white_processing(frame, camera.grayscale_split_value)
        
        cv.imshow(camera.name, black_white_frame)

        white_pixel_count = np.sum(black_white_frame) / 255

        segment_number = self.check_segments(black_white_frame, camera.amount_of_segments)

        cv.setWindowTitle(camera.name, f"{camera.name}: White line detected = {bool(segment_number)}" + (f", In segment {camera.name} = {segment_number}" if segment_number else ""))

        data ={
            "camera": camera.name,
            "steering_percentage": segment_number / camera.amount_of_segments,
            "segment": segment_number
        }

        self.child_pipe.send(data)
   
        if camera.remaining_calibration_frame_buffer:
            if camera.white_pixel_calibration_value-white_pixel_count<-100 or camera.white_pixel_calibration_value-white_pixel_count>100:
                camera.grayscale_split_value=self.calibrate_grayscale_split_value(camera.remaining_calibration_frame_buffer, camera.grayscale_split_value, camera.white_pixel_calibration_value, white_pixel_count)
            camera.remaining_calibration_frame_buffer-=1


    def handle_keyboard_input(self, camera):
        pressed_key = cv.waitKey(1)
        if pressed_key <= 0: return
        match chr(pressed_key):
            case camera.keybind_plus_one: camera.grayscale_split_value += 1
            case camera.keybind_minus_one: camera.grayscale_split_value -= 1
            case camera.keybind_plus_ten: camera.grayscale_split_value += 10
            case camera.keybind_minus_ten: camera.grayscale_split_value -= 10
            case camera.keybind_auto_calibrate:
                camera.remaining_calibration_frame_buffer = 7
                camera.grayscale_split_value=127
            case 'q': self.running = False
            
        if camera.grayscale_split_value < 0: camera.grayscale_split_value = 0
        if camera.grayscale_split_value > 255: camera.grayscale_split_value = 255

class Camera:
    
    def __init__(self, camera_name, camera_device, white_pixel_calibration_value, amount_of_segments,
                 keybind_plus_one, keybind_minus_one, keybind_plus_ten,
                 keybind_minus_ten, keybind_auto_calibrate, grayscale_split_value=100) -> None:

        self.name=camera_name
        self.cap=cv.VideoCapture(camera_device, cv.CAP_DSHOW)
        self.white_pixel_calibration_value=white_pixel_calibration_value 
        self.keybind_plus_one = keybind_plus_one,
        self.keybind_minus_one = keybind_minus_one,
        self.keybind_plus_ten = keybind_plus_ten,
        self.keybind_minus_ten = keybind_minus_ten, 
        self.keybind_auto_calibrate = keybind_auto_calibrate
        self.amount_of_segments = amount_of_segments
        self.grayscale_split_value = grayscale_split_value
        self.remaining_calibration_frame_buffer=0

