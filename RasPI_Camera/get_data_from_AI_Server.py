####################################
# Project : Zerothone Dankook Univ.
# Created : Yoonchul Chung
# Date    : 2025.03.29
####################################
from flask import Flask, jsonify, request
import RPi.GPIO as GPIO
import signal
import sys

import pytz
from datetime import datetime
from colorama import Fore

app = Flask(__name__)

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def get_current_korean_time():

    korea_tz = pytz.timezone('Asia/Seoul')
    now_korea = datetime.now(korea_tz)
    return now_korea.strftime('%Y-%m-%d %H:%M:%S')

def print_log(status, message):
    
    korea_tz  = pytz.timezone('Asia/Seoul')
    now_korea = datetime.now(korea_tz)
    kst_time  =  now_korea.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    if status == 'active':
        print(Fore.GREEN + "[SERVER] " + str(kst_time) + " : " + str(message) + Fore.RESET)
        
    elif status == 'error':
        print(Fore.RED + "[SERVER] " + str(kst_time) + " : " + str(message) + Fore.RESET)

    elif status == 'info':
        print(Fore.BLUE + "[SERVER] " + str(kst_time) + " : " + str(message) + Fore.RESET)
        
#########################################################################################################
# Setting
#########################################################################################################

# X_PIN_1 | X_PIN_0
X_PIN_0 = 20
X_PIN_1 = 21

# Y Pin is broken .....

# Y_PIN_1 | Y_PIN_0
#Y_PIN_0 = 26
#Y_PIN_1 = 19

GPIO.setmode(GPIO.BCM)

GPIO.setup(X_PIN_0, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(X_PIN_1, GPIO.OUT, initial=GPIO.LOW)

#GPIO.setup(Y_PIN_0, GPIO.OUT, initial=GPIO.LOW)
#GPIO.setup(Y_PIN_1, GPIO.OUT, initial=GPIO.LOW)

gpio_cleaned_up = False
        
def cleanup_gpio(signum=None, frame=None):
    global gpio_cleaned_up
    
    if gpio_cleaned_up:
        return
    print_log('info', "clean up GPIO ...")
    
    try:
        GPIO.output(X_PIN_0, GPIO.LOW)
        GPIO.output(X_PIN_1, GPIO.LOW)
        
        #GPIO.output(Y_PIN_0, GPIO.LOW)
        #GPIO.output(Y_PIN_1, GPIO.LOW)
        
    except RuntimeError as e:
        print_log('error', f"Something Wrong to Setting GPIO output : {e}")
        
    GPIO.cleanup()
    gpio_cleaned_up = True
    print_log('info', "Finsed to clean GPIO")
    if signum is not None:
        sys.exit(0)

signal.signal(signal.SIGINT, cleanup_gpio)
signal.signal(signal.SIGTERM, cleanup_gpio)


X_PIN_0_STATE = 0
X_PIN_1_STATE = 0

#Y_PIN_0_STATE = 0
#Y_PIN_1_STATE = 0

########################################################
# Main
########################################################
@app.route('/', methods=['POST'])
def home():
    
    global X_PIN_0_STATE, X_PIN_1_STATE
    #global Y_PIN_0_STATE, Y_PIN_1_STATE

    form_data = request.get_json()
    
    if form_data is None:
        return jsonify({"message": "WRONG Request!. Send JSON FILE."}), 400
    
    x_coordinate = form_data.get('x')
    y_coordinate = form_data.get('y')
    
    if x_coordinate is None or y_coordinate is None:
        return jsonify({"message": "SEND X and Y Coordinate"}), 400
    
    try:
        x = float(x_coordinate)
        y = float(y_coordinate)
    except (ValueError, TypeError):
        return jsonify({"message": "X and Y Coordinate should be number"}), 400
    
    # X_PIN_1 | X_PIN_0
            
    if x > 0:
                    
        X_PIN_0_STATE = GPIO.HIGH
        X_PIN_1_STATE = GPIO.LOW
    
    elif x < 0 :
        
        X_PIN_0_STATE = GPIO.LOW
        X_PIN_1_STATE = GPIO.HIGH
            
    else:
        
        X_PIN_0_STATE = GPIO.LOW
        X_PIN_1_STATE = GPIO.LOW
        
    # y pin is broken....
    # if y > 0:
        
    #     Y_PIN_0_STATE = GPIO.HIGH
    #     Y_PIN_1_STATE = GPIO.LOW
        
    # elif y < 0 :
    
    #     Y_PIN_0_STATE = GPIO.LOW
    #     Y_PIN_1_STATE = GPIO.HIGH  
    # else:
    #     Y_PIN_0_STATE = GPIO.LOW
    #     Y_PIN_1_STATE = GPIO.LOW
    
    ##########################################
    # Send Bit to RasPi HW
    ##########################################

    print_log('active', "!!!!!SENT BIT!!!!!")
    
    GPIO.output(X_PIN_0, X_PIN_0_STATE)
    GPIO.output(X_PIN_1, X_PIN_1_STATE)
    
    #GPIO.output(Y_PIN_0, Y_PIN_0_STATE)
    #GPIO.output(Y_PIN_1, Y_PIN_1_STATE)
        
    return jsonify({"message": "GOOD"})


########################################################
# Clear Servo Pin
########################################################
@app.route('/reset_servo', methods=['POST'])
def reset_servo():
    
    GPIO.output(X_PIN_0, GPIO.LOW)
    GPIO.output(X_PIN_1, GPIO.LOW)
    
    #GPIO.output(Y_PIN_0, GPIO.LOW)
    #GPIO.output(Y_PIN_1, GPIO.LOW)
    
    print_log('error', "[RESET] RESET PIN_0 and PIN_1 to 0")
    
    return jsonify({"message" : "GOOD TO RESET"})


@app.route('/not_detected', methods=['POST'])
def not_detected():
            
    global X_PIN_0_STATE, X_PIN_1_STATE
    #global Y_PIN_0_STATE, Y_PIN_1_STATE
            
    X_PIN_0_STATE = GPIO.HIGH
    X_PIN_1_STATE = GPIO.HIGH
    
    #Y_PIN_0_STATE = GPIO.HIGH
    #Y_PIN_1_STATE = GPIO.HIGH

        
    GPIO.output(X_PIN_0, X_PIN_0_STATE)
    GPIO.output(X_PIN_1, X_PIN_1_STATE)
    
    #GPIO.output(Y_PIN_0, Y_PIN_0_STATE)
    #GPIO.output(Y_PIN_1, Y_PIN_1_STATE)
    
    print_log('error', "[Not Detected] PIN_0 and PIN_1 to 0")
    
    return jsonify({"message" : "GOOD TO RESET"})



###########################################################################
if __name__ == '__main__':
    
    try:
        print_log('info', "Running FLASK Server")
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print_log('error', f"Something Wrong to Server {e}")
    finally:
        cleanup_gpio()
