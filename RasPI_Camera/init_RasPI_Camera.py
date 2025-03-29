####################################
# Project : Zerothone Dankook Univ.
# Created : Yoonchul Chung
# Date    : 2025.03.29
####################################
import RPi.GPIO as GPIO
import subprocess
import time

import requests

import pytz
from datetime import datetime
from colorama import Fore

def get_current_korean_time():

    korea_tz = pytz.timezone('Asia/Seoul')
    now_korea = datetime.now(korea_tz)
    return now_korea.strftime('%Y-%m-%d %H:%M:%S')

def print_log(status, message):
    
    korea_tz  = pytz.timezone('Asia/Seoul')
    now_korea = datetime.now(korea_tz)
    kst_time  =  now_korea.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    if status == 'active':
        print(Fore.GREEN + "[MAIN]   " + str(kst_time) + " : " + str(message) + Fore.RESET)
        
    elif status == 'error':
        print(Fore.RED + "[MAIN]   " + str(kst_time) + " : " + str(message) + Fore.RESET)

    elif status == 'info':
        print(Fore.BLUE + "[MAIN]   " + str(kst_time) + " : " + str(message) + Fore.RESET)
        
INTERRUPT_PIN = 17

run_send_cam = ["python", "send_camera_to_AI_Server.py"]
run_adc_led  = ["python", "detect_adc.py"]
run_server   = ["python", "get_data_from_AI_Server.py"]

process_send_cam = None
process_run_adc  = None
process_server   = None

GPIO.setmode(GPIO.BCM)
GPIO.setup(INTERRUPT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def reset_connector():
    url = "http://192.168.0.2:5000/reset_servo"
    headers = {"Content-Type": "application/json"}

    data = {"face": True,
            'x' :0,
            'y' :0,
            'message' : "Reset",
            }
    
    response = requests.post(url, json=data)
    
    
def ISR_PIN(channel):
    global process_send_cam
    global process_run_adc
    global process_server

    #########################
    # Run FIlE 
    #########################
    if GPIO.input(INTERRUPT_PIN) == GPIO.HIGH:
        '''
            This works when interrupt bit is 1
        '''
        if (process_send_cam is None and 
            process_run_adc is None and 
            process_server is None):

            
            print_log('active', "Running [send_camera_to_AI_Server.py, detect_adc.py, and get_data_from_AI_Server.py]...")
            try:
                process_send_cam = subprocess.Popen(run_send_cam)
                print_log('active', f"send_camera_to_AI_Server.py started with PID: {process_send_cam.pid}")
                
                process_run_adc = subprocess.Popen(run_adc_led)
                print_log('active', f"detect_adc.py started with PID: {process_run_adc.pid}")
                
                process_server = subprocess.Popen(run_server)
                print_log('active', f"get_data_from_AI_Server.py started with PID: {process_server.pid}")
            except Exception as e:
                print_log('error', f"Failed to start processes: {e}")

                if process_send_cam:
                    process_send_cam.terminate()
                    process_send_cam = None
                if process_run_adc:
                    process_run_adc.terminate()
                    process_run_adc = None
                if process_server:
                    process_server.terminate()
                    process_server = None

    #########################
    # Stop FIlE 
    #########################
    elif GPIO.input(INTERRUPT_PIN) == GPIO.LOW:
        '''
            This works when interrupt bit is 0
        '''
        
        if (process_send_cam is not None or 
            process_run_adc is not None or 
            process_server is not None):

            print_log('info', "Stopping [send_camera_to_AI_Server.py, detect_adc.py, and get_data_from_AI_Server.py]...")
            try:
                if process_send_cam is not None:
                    process_send_cam.terminate()  
                    process_send_cam.wait(timeout=5) 
                    print_log('active', "send_camera_to_AI_Server.py terminated gracefully.")
                    process_send_cam = None
            except subprocess.TimeoutExpired:
                print_log('active', "send_camera_to_AI_Server.py did not terminate in time. Forcing kill...")
                process_send_cam.kill()  
                process_send_cam.wait()
                print_log('info', "send_camera_to_AI_Server.py killed.")
                process_send_cam = None
            except Exception as e:
                print_log('info', f"Error terminating send_camera_to_AI_Server.py: {e}")
                process_send_cam = None

            try:
                if process_run_adc is not None:
                    process_run_adc.terminate() 
                    process_run_adc.wait(timeout=5)
                    print_log('info', "detect_adc.py terminated gracefully.")
                    process_run_adc = None
            except subprocess.TimeoutExpired:
                print_log('error', "detect_adc.py did not terminate in time. Forcing kill...")
                process_run_adc.kill()
                process_run_adc.wait()
                print_log('info', "detect_adc.py killed.")
                process_run_adc = None
            except Exception as e:
                print_log('error', f"Error terminating detect_adc.py: {e}")
                process_run_adc = None

            try:
                reset_connector()
                if process_server is not None:
                    process_server.terminate()
                    process_server.wait(timeout=5)
                    print_log('info', "get_data_from_AI_Server.py terminated gracefully.")
                    process_server = None
            except subprocess.TimeoutExpired:
                print_log('error', "get_data_from_AI_Server.py did not terminate in time. Forcing kill...")
                process_server.kill()
                process_server.wait()
                print_log('info', "get_data_from_AI_Server.py killed.")
                process_server = None
            except Exception as e:
                print(f"Error terminating get_data_from_AI_Server.py: {e}")
                process_server = None

def main():
    
    global process_send_cam, process_run_adc, process_server
    
    try:
        print_log('info', "Waiting for interrupt on GPIO pin 17...")
        GPIO.add_event_detect(INTERRUPT_PIN, GPIO.BOTH, callback=ISR_PIN, bouncetime=300)

        while True:
            time.sleep(1)  # CPU funny time
    except KeyboardInterrupt:
        print_log('info', "KeyboardInterrupt received. Exiting program.")
    finally:

        #################################################
        # This is for Send Camera Data to Server
        #################################################
        if process_send_cam is not None:
            print_log('info', "Cleaning up send_camera_to_AI_Server.py process...")
            try:
                process_send_cam.terminate()
                process_send_cam.wait(timeout=5)
                print_log('info', "send_camera_to_AI_Server.py terminated gracefully.")
            except subprocess.TimeoutExpired:
                print_log('error', "send_camera_to_AI_Server.py did not terminate in time. Forcing kill...")
                process_send_cam.kill()
                process_send_cam.wait()
                print_log('info', "send_camera_to_AI_Server.py killed.")
            except Exception as e:
                print_log('error', f"Error terminating send_camera_to_AI_Server.py: {e}")
            finally:
                process_send_cam = None

        #################################################
        # This is for ADC convert
        #################################################
        if process_run_adc is not None:
            print_log('info', "Cleaning up detect_adc.py process...")
            try:
                process_run_adc.terminate()
                process_run_adc.wait(timeout=5)
                print_log('info', "detect_adc.py terminated gracefully.")
            except subprocess.TimeoutExpired:
                print_log('error', "detect_adc.py did not terminate in time. Forcing kill...")
                process_run_adc.kill()
                process_run_adc.wait()
                print_log('info', "detect_adc.py killed.")
            except Exception as e:
                print_log('error', f"Error terminating detect_adc.py: {e}")
            finally:
                process_run_adc = None

        #########################################################
        # This is for get AI face detected data from AI Server
        #########################################################
        if process_server is not None:
            print_log('info', "Cleaning up get_data_from_AI_Server.py process...")
            try:
                process_server.terminate()
                process_server.wait(timeout=5)
                print_log('info', "get_data_from_AI_Server.py terminated gracefully.")
            except subprocess.TimeoutExpired:
                print_log('error', "get_data_from_AI_Server.py did not terminate in time. Forcing kill...")
                process_server.kill()
                process_server.wait()
                print_log('info', "get_data_from_AI_Server.py killed.")
            except Exception as e:
                print_log('error', f"Error terminating get_data_from_AI_Server.py: {e}")
            finally:
                process_server = None

        GPIO.cleanup() 
        print_log('info', "GPIO cleaned up. Program exited.")

if __name__ == "__main__":
    main()
