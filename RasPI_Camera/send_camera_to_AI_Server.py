####################################
# Project : Zerothone Dankook Univ.
# Created : Yoonchul Chung
# Date    : 2025.03.29
####################################
import requests
import subprocess
import signal
import time
import threading

import pytz
from datetime import datetime
from colorama import Fore

server_base = 'http://192.168.0.2:2090'

def get_current_korean_time():

    korea_tz = pytz.timezone('Asia/Seoul')
    now_korea = datetime.now(korea_tz)
    return now_korea.strftime('%Y-%m-%d %H:%M:%S')



def print_log(status, message):
    
    korea_tz  = pytz.timezone('Asia/Seoul')
    now_korea = datetime.now(korea_tz)
    kst_time  =  now_korea.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    if status == 'active':
        print(Fore.GREEN + "[CAMERA] " + str(kst_time) + " : " + str(message) + Fore.RESET)
        
    elif status == 'error':
        print(Fore.RED + "[CAMERA]" + str(kst_time) + " : " + str(message) + Fore.RESET)



####################################################################################
def send2server_post(url=server_base, data=None):
    try:
        response = requests.post(url=url, data=data)
        print_log("active", f"Send Data to {url}")
        return response
    except requests.RequestException as e:
        print_log('error', f"Error sending POST request: {e}")
        return None



def capture_video2server(stop_event):
        
    url = f'{server_base}/face_detect'
    print_log('info', "Start To capture Video")

    command = [
        "libcamera-vid",
        "-t", "0",                       # Inifinite Streaming
        "--inline",                      # Encoding -> Streaming
        "--width", "640", "--height", "640",
        "--framerate", "20",
        "--codec", "mjpeg",              # Streaming Type : MJPEG
        "-o", "-"                        # Standard Streaming
    ]

    jpeg_start = b'\xff\xd8'
    jpeg_end = b'\xff\xd9'

    buffer = b''

    try:
        ###################################
        # Start to Capture Video
        ###################################
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0) as process:
            while not stop_event.is_set():
                data = process.stdout.read(4096)
                if not data:
                    break

                buffer += data

                while True:
                    start_idx = buffer.find(jpeg_start)
                    end_idx = buffer.find(jpeg_end, start_idx)

                    if start_idx != -1 and end_idx != -1:

                        frame = buffer[start_idx:end_idx + 2]
                        buffer = buffer[end_idx + 2:]
                        
                        response = send2server_post(url=url, data=frame)

                        if response is None:
                            print_log("error", "Failed to send frame to server.")
                    else:
                        break
    except Exception as e:
        print_log("error", f"Error during video capture: {e}")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
                print_log("active", "libcamera-vid terminated gracefully.")
            except subprocess.TimeoutExpired:
                print_log("active", "libcamera-vid did not terminate in time. Killing process.")
                process.kill()
                process.wait()
        print_log("active", "Video capture stopped.")


def signal_handler(signum, frame):
    print_log("active", "Received termination signal. Exiting gracefully...")
    stop_event.set()



def main():
    global stop_event
    stop_event = threading.Event()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    video_thread = threading.Thread(target=capture_video2server, args=(stop_event,))
    video_thread.start()

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except Exception as e:
        print_log("error", f"Main thread error: {e}")
    finally:
        stop_event.set()
        video_thread.join()
        print_log('info', "send_camera_to_AI_Server.py has exited.")



################################################################################################
if __name__ == "__main__":
    command = ['clear']
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print_log('error', f"Wrong : {e}")

    print_log('info', "=WELCOME TO 2025 Zerothone=")
    main()
