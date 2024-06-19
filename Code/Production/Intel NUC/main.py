from ESP import ESP32 
from YOLO_easyOCR.YOLOv8 import ObjectDetection
from lineDetection.lines import Detection
from multiprocessing import Process, Pipe
import time
import easyocr
import threading
import os

def driving_algorithm(parsed_data):
    global des_speed
    global waiting_on_green_light
    global waiting_on_pedestrian
    global person_crossing_done
    global person_segment_count

    if not "Red" in parsed_data and not "Person" in parsed_data: print(f"driving at {des_speed} km/h")


    if waiting_on_green_light and "Green" in parsed_data and not "Red" in parsed_data:
        print("Green light seen, driving")
        des_speed = sign_speed
        waiting_on_green_light = False

    if not waiting_on_green_light: 
        des_speed = sign_speed
    else: 
        print("Waiting on green light")
        return

    if "Red" in parsed_data:
        if not waiting_on_green_light:
            print("Red light seen, driving slowly") 
            des_speed = 5
        if front_camera_segment >= 2:
            print("Red light and line seen, stopping")
            des_speed = 0
            waiting_on_green_light = True

    if "Person" in parsed_data:
        global start_segment
        if not waiting_on_pedestrian:
            start_segment = last_known_object_state["Person"]
            des_speed = 5
        else: des_speed = 0

        # stop crossing
        if waiting_on_pedestrian and last_known_object_state["Person"] != start_segment and (last_known_object_state["Person"] == 1 or last_known_object_state["Person"] == person_segment_count) :
            print("Person crossed, start driving")
            des_speed = sign_speed
            waiting_on_pedestrian = False
            person_crossing_done = True

        # start crossing
        if not waiting_on_pedestrian and not person_crossing_done:
            if front_camera_segment:
                des_speed = 0
                waiting_on_pedestrian = True
                start_segment = last_known_object_state["Person"]
                print(f"Person and crosswalk seen, stop driving, startSegment = {start_segment}")
            else: print("Person but no crosswalk seen")

        if person_crossing_done: print("Person seen but person crossing done, so driving")
    

    elif waiting_on_pedestrian or person_crossing_done: reset_crossing()

def steering_logic(): # run in thread
    while True:

        if bool(left_camera_steering_percentage) and not bool(right_camera_steering_percentage):
            esp32_data["steering_degrees"] = int(left_camera_steering_percentage * (steering_range / 2) + (steering_range / 2))
            continue

        if not bool(left_camera_steering_percentage) and bool(right_camera_steering_percentage):
            esp32_data["steering_degrees"] = int(right_camera_steering_percentage * (steering_range / 2))
            continue

        esp32_data["steering_degrees"] = 90

def send_kart_control_data(): # run in thread
    while True:
        esp32_parent_pipe.send(esp32_data)
        time.sleep(0.005)

def ocr_detect(outer_most_sign, result):
    x_min, y_min, x_max, y_max = outer_most_sign
    roi = result.orig_img[int(y_min):int(y_max), int(x_min):int(x_max)]  # crop frame using bb cords
    for (bbox, text, prob) in easy_ocr_reader.readtext(roi):
        print(text)
        return text
    
def parseobject_detection_data():
    global last_known_object_state
    global result_history
    global sign_speed
    global current_person_segment
    global person_segment_count
    global object_detection_data

    current_person_segment = 0
    outer_most_red_light = 0
    outer_most_green_light = 0
    outer_most_sign = 0
    person_box = [0, 0, 0, 0]

    detected_classes_set = set()

    for i, c in enumerate(object_detection_data.boxes.cls):
        class_name = object_detection_data.names[int(c)]
        detected_classes_set.add(class_name)
        coords = object_detection_data.boxes.xyxy[i].tolist()
        normalized_coords = object_detection_data.boxes.xyxyn[i]
        max_x_coord = coords[2]
        match class_name:
            case "Red":
                if max_x_coord > outer_most_red_light: outer_most_red_light = max_x_coord

            case "Green":
                if max_x_coord > outer_most_green_light: outer_most_green_light = max_x_coord
            
            case "Sign":
                if not outer_most_sign:
                    outer_most_sign = coords
                if max_x_coord > outer_most_sign[2]:         # compare x_max
                    outer_most_sign = coords
            case "Person":
                if ((person_box[2]-person_box[0])*(person_box[3]-person_box[1]) < (normalized_coords[2]-normalized_coords[0])*(normalized_coords[3]-normalized_coords[1])):
                    person_box = normalized_coords
                current_person_segment = normal_to_segment(person_segment_count, person_box[0]+(person_box[2]-person_box[0])/2)

    if outer_most_sign != 0:
        tmp_sign_speed = ocr_detect(outer_most_sign, object_detection_data)
        if tmp_sign_speed in ["10","15","20"]:
            sign_speed = tmp_sign_speed

    if len(result_history) == result_history_size:
        result_history.pop(result_history_size - 1)
    result_history.insert(0, detected_classes_set)

    
    filtered_set = low_pass_filter(object_detection_data.names.values(), result_history, 0.5)

    if outer_most_red_light: last_known_object_state["Red"] = outer_most_red_light
    if outer_most_green_light: last_known_object_state["Green"] = outer_most_green_light
    if outer_most_sign: last_known_object_state["Sign"] = outer_most_sign
    if current_person_segment: last_known_object_state["Person"] = current_person_segment

    return_data = {}
    for object in filtered_set:
        if object == "Yellow": continue
        return_data[object] = last_known_object_state[object]

    return return_data
    
def low_pass_filter(valid_class_names, result_history, hit_percentage):
    filtered_set = set()
    result_history_length = len(result_history)
    for class_name in valid_class_names:
        registered_object_frames = sum(class_name in history_frame for history_frame in result_history)
        if registered_object_frames / result_history_length > hit_percentage:
            filtered_set.add(class_name)
    return filtered_set

def normal_to_segment(segment_count, normalized_box_center):
    return int(normalized_box_center*segment_count) + 1

def reset_crossing():
    global waiting_on_pedestrian
    global person_crossing_done
    global start_segment
    global last_known_object_state

    waiting_on_pedestrian = False # is true while a person is crossing
    person_crossing_done = False # is true after a person has crossed and resets when no person detected
    start_segment = -1 # segment where person is first detected

    print("crossing reset")

def yolo_start():
    global object_detection_data
    global easy_ocr_reader
    object_detection_data = None

    yolov8_parent_pipe, yolov8_child_pipe = Pipe()

    yolov8_process = Process(target=ObjectDetection().detect, args=(yolov8_child_pipe,), daemon=True)
    yolov8_data_thread = threading.Thread(target=get_process_data, args=(yolov8_parent_pipe, "yolov8"))
    easy_ocr_reader = easyocr.Reader(['en'], gpu=False)

    yolov8_process.start()
    yolov8_data_thread.start()

    while object_detection_data is None:
        pass

def esp32_start():
    global esp32_parent_pipe
    esp32_parent_pipe, esp32_child_pipe = Pipe()

    esp32_process = Process(target=ESP32().connect, args=(esp32_child_pipe,))
    esp32_sending_thread = threading.Thread(target=send_kart_control_data)
    gas_control_thread = threading.Thread(target=gas_brake_algorithm)

    gas_control_thread.start()
    esp32_sending_thread.start()
    esp32_process.start()

def line_detection_start():
    global front_camera_segment
    global left_camera_steering_percentage
    global right_camera_steering_percentage

    front_camera_segment = 0
    left_camera_steering_percentage = 0
    right_camera_steering_percentage = 0

    lineDetection_parent_pipe, lineDetection_child_pipe = Pipe()

    line_detection_process = Process(target=Detection().run, args=(lineDetection_child_pipe,), daemon=True)
    line_detection_process.start()

    line_detection_data_thread = threading.Thread(target=get_process_data, args=(lineDetection_parent_pipe, "lineDetection"))
    steering_logic_thread = threading.Thread(target=steering_logic,)

    steering_logic_thread.start()
    line_detection_data_thread.start()

    while front_camera_segment is None:
        pass

def get_process_data(parent_pipe, process):
    while True:
        if parent_pipe.poll(None):
            data = parent_pipe.recv()
            # print(data)
            match process:
                case "lineDetection":
                    global left_camera_steering_percentage
                    global right_camera_steering_percentage
                    global front_camera_segment
                    if data["camera"] == "voor": front_camera_segment = data["segment"]
                    if data["camera"] == "links": left_camera_steering_percentage = data["steering_percentage"]
                    if data["camera"] == "rechts": right_camera_steering_percentage = data["steering_percentage"]

                case "yolov8":
                    global object_detection_data
                    object_detection_data = data
                    driving_algorithm(parseobject_detection_data())
                    gas_brake_algorithm()
                case "revolutions":
                    global revs
                    revs  = data
            send_kart_control_data()

def gas_brake_algorithm():
    global des_speed
    global cur_speed
    # motor_PWM  = 0
    # brake_PWM = 0

    if des_speed > 0:
        esp32_data["motor_PWM"] = 255
        esp32_data["brake_PWM"] = 0
    if des_speed == 0:
        esp32_data["motor_PWM"] = 0
        esp32_data["brake_PWM"] = 255

    # curSpeed = berekening met revs
    # if des > curspeed bla bla curve

    #  bla bla bereken hoeveel brake_PWM als nodig

    # esp32_data["motor_PWM"] = motor_PWM
    # if brake_PWM: esp32_data["brake_PWM"] = brake_PWM

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    last_known_object_state = {}
    waiting_on_green_light = False
    sign_speed = 10
    cur_speed = 0
    des_speed = 10
    steering_range = 180
    result_history = [] 
    result_history_size = 60

    left_camera_steering_percentage = 0
    right_camera_steering_percentage = 0
    front_camera_segment = 0

    waiting_on_pedestrian = False # is true while a person is crossing
    person_crossing_done = False # is true after a person has crossed and resets when no person detected
    start_segment = -1 # segment where person is first detected
    current_person_segment = -1
    person_segment_count = 4

    esp32_data = {
        "motor_PWM": 0,
        "brake_PWM": 0,
        "steering_degrees": 90
    }
    
    esp32_start()
    yolo_start()
    line_detection_start()
