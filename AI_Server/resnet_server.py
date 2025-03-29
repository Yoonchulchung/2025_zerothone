from flask import Flask
from flask import Flask, Response, request, stream_with_context
from colorama import Fore
import requests

import numpy as np
import cv2
import os
import subprocess

OUTPUT_DIR = "output_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)


import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def print_log(status, message):
    
    if status == 'active':
        print("-----------------------------")
        print(Fore.GREEN + message + Fore.RESET)
        print("-----------------------------")
        
    elif status == 'error':
        print("-----------------------------")
        print(Fore.RED + message + Fore.RESET)
        print("-----------------------------")
        
    elif status == 'info':
        print("-----------------------------")
        print(Fore.BLUE + message + Fore.RESET)
        print("-----------------------------")


def check_opencv_cuda():
    cuda_device_count = cv2.cuda.getCudaEnabledDeviceCount()
    print_log('info', f"Number of CUDA : {cuda_device_count}")

    if cuda_device_count > 0:
        for i in range(cuda_device_count):
            print_log('info', f"Device {i}: Available to Use")
    else:
        print_log('error', "CUD is not Available")


frame_data = b''

MODEL_FILE = "./models/res10_300x300_ssd_iter_140000.caffemodel"
CONFIG_FILE = "./models/deploy.prototxt.txt"

# MODEL_FILE = "./MobileNetSSD_deploy.caffemodel"
# CONFIG_FILE = "deploy_mobilenet.prototxt"

# CONFIG_FILE = "yolov3-tiny.cfg"
# MODEL_FILE = "yolov3-tiny.weights"

# net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, MODEL_FILE)
# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)


net = cv2.dnn.readNetFromCaffe(CONFIG_FILE, MODEL_FILE)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)


def frame_data_to_numpy(frame_data):

    np_array = np.frombuffer(frame_data, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Failed to decode JPEG image")
    
    return img
    
    
def is_valid_jpeg(frame_data):
    return frame_data.startswith(b'\xff\xd8') and frame_data.endswith(b'\xff\xd9')


def clean_frame_data(frame_data):

    if not frame_data.startswith(b'\xff\xd8'):
        frame_data = b'\xff\xd8' + frame_data
    if not frame_data.endswith(b'\xff\xd9'):
        frame_data += b'\xff\xd9'
    return frame_data
    

def display_or_save_image(image, save_path="./received_image.jpg"):
    
    if image is not None:
        output_path = os.path.join(OUTPUT_DIR, 'processed_image.jpg')
        cv2.imwrite(output_path, image)
        
    else:
        print("Invalid image. Unable to display or save.")
        
        
def detect_face(img, confidence_threshold=0.5, type='resnet'):
    if img is None:
        raise ValueError("Invalid image: Unable to decode the input image")

    h, w = img.shape[:2]

    if type == 'resnet':
        blob = cv2.dnn.blobFromImage(img, scalefactor=1.0, size=(300, 300), 
                                    mean=(104.0, 177.0, 123.0), swapRB=False, crop=False)
        net.setInput(blob)

    elif type == 'yolo':
        blob = cv2.dnn.blobFromImage(img, scalefactor=1/255.0, size=(416, 416), swapRB=True, crop=False)
        net.setInput(blob)

    detections = net.forward()


    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            
            # Calc Face Coord.
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x1, y1) = box.astype("int")
            faces.append((x, y, x1 - x, y1 - y))
            
            cv2.rectangle(img, (x, y), (x1, y1), (0, 255, 0), 2)
            text = f"{confidence:.2f}"
            cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imwrite("detected_faces.jpg", img)
    return faces


def extract_frames(mjpeg_data):

    def clean_mjpeg_data(mjpeg_data):
        
        if not mjpeg_data.startswith(b'\xff\xd8'):
            mjpeg_data = b'\xff\xd8' + mjpeg_data
        if not mjpeg_data.endswith(b'\xff\xd9'):
            mjpeg_data += b'\xff\xd9'
        return mjpeg_data

    mjpeg_data = clean_mjpeg_data(mjpeg_data)

    frames = []
    start = 0
    while True:
        start = mjpeg_data.find(b'\xff\xd8', start)
        end = mjpeg_data.find(b'\xff\xd9', start)
        if start == -1 or end == -1:
            break
        frame = mjpeg_data[start:end + 2]
        frames.append(frame)
        start = end + 2
    return frames


def parse_image(mjpeg_data):
    
    if not mjpeg_data:
        print_log('error', "MJPEG data is empty or None")
        return
    
    frames = extract_frames(mjpeg_data)

    for frame_data in frames:

        # JPEG DECODE
        np_array = np.frombuffer(frame_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if image is None:
            print("Failed to decode image")
            continue
        
        # RUN DETECT
        faces = detect_face(image)
        display_or_save_image(image, save_path="./received_frame.jpg")


    if len(frame_data) > 1000000:
        frame_data = frame_data[-1000000:]
        
    return faces


def find_center_from_image(faces):
    """
        Center is 250, 250
        X Coordinate = faces[0]
        Y Coordinate = faces[1]
        
        Width  = faces[2]
        Height = faces[3]
    """
    
    x_coord, y_coord, width, hegith = faces[0]
    
    
    center_x = x_coord + width  // 2
    center_y = y_coord + hegith // 2    
    
    print_log('active', f'center x : {center_x}, center y : {center_y}')
    return center_x, center_y
    
    
def find_movement(x, y):
    x = 250 - x
    y = 250 - y
    
    return x, y


# Filter Constant (0 < alpha < 1)
ALPHA = 0.5
filtered_x = None
filtered_y = None

def send_2_other_raspi(x, y, url):
    global filtered_x, filtered_y
    
    current_x = int(x)
    current_y = int(y)
    
    if filtered_x is None:
        filtered_x = current_x
        filtered_y = current_y
    else:
        # LPF
        filtered_x = ALPHA * current_x + (1 - ALPHA) * filtered_x
        filtered_y = ALPHA * current_y + (1 - ALPHA) * filtered_y
    
    data = {
        'face': True,
        'x': int(filtered_x / 5),
        'y': int(filtered_y / 5),
    }
    
    print_log('active', f'move x : {filtered_x / 5}, move y : {filtered_y / 5}')

    try:
        response = requests.post(url=url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        response = None
    
    return response

def send_not_detected(url):
    data = {
        "MESSAGE" : "Not Detected",
    }
    response = requests.post(url=url, json=data)
    return response

        
#=================== MAIN ===================
@app.route('/face_detect', methods=['post'])
def main():
    
    url = "http://192.168.0.4:5000/"

    global frame_data
    
    mjpeg_data = request.data
    
    # Input Data Size is 500 x 500
    faces = []
    faces = parse_image(mjpeg_data)
    
    
    if not faces:
        url_ = url + "not_detected"
        
        response  = send_not_detected(url_)
        
        print_log('error', "Nothing is Detected")
        return "MJPEG data is empty or None", 400
    
    # Center is 250, 250
    x, y = find_center_from_image(faces)    
    x, y = find_movement(x, y)

    response  = send_2_other_raspi(x, y, url)
    
    return "Frame received", 200
    
    
if __name__ == '__main__':

    command = [
    'clear'
    ]
    
    try:
        subprocess.run(command, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Wrong : {e}")
        
    print_log("active", "= WELCOME TO 2025 Zerothone =")
    check_opencv_cuda()

    app.run(host='0.0.0.0', port=2090, debug=True)


                                                                          