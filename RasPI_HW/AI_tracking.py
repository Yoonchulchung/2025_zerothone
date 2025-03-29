#!/usr/bin/python

from table_mode import write_table_mode
import logging
import RPi.GPIO as GPIO
import time
import threading
import sys
import os
import select
from datetime import datetime, timedelta
import signal

log = logging.getLogger('werkzeug')
log.disabled = True
from colorama import Fore

# 초기 시간 설정
start_time = datetime.now()

# file_name
file_table_setting = "./table_setting.py"

# GPIO pin and initial setup
servo_pin_x = 23
servo_pin_y = 24
input_pin_btn = 18
communication_pin_x_0 = 17
communication_pin_x_1 = 27
communication_pin_y_0 = 6
communication_pin_y_1 = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin_x, GPIO.OUT)
GPIO.setup(servo_pin_y, GPIO.OUT)
GPIO.setup(input_pin_btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(communication_pin_x_0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(communication_pin_x_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(communication_pin_y_0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(communication_pin_y_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# PWM initialization
pwm_x = GPIO.PWM(servo_pin_x, 50)
pwm_y = GPIO.PWM(servo_pin_y, 50)
pwm_x.start(7.5) 
pwm_y.start(7.5)

# Servo motor current angle tracking
current_angle_x = 0 
current_angle_y = 0
MIN_ANGLE = -90
MAX_ANGLE = 90
direction_x = 0
direction_y = 0
delay_factor = 0.02 

# Program running, coordinate state flag
running_x = True
running_y = True
x_coordinate = 0
y_coordinate = 0
object_detect = False

# endflag
END_FLAG = 0

# 인터럽트 발생 시 실행될 콜백 함수
def ISR_btn(channel):
    global END_FLAG, object_detect
    print("btn detected on pin:", channel)
    write_table_mode(2, "btn_on")
    END_FLAG = 1
    if object_detect == True:
        print("Setting the table")
        os.system(file_table_setting)
        print("Setting is cleared")


# 인터럽트 설정 
GPIO.add_event_detect(input_pin_btn, GPIO.RISING, callback=ISR_btn, bouncetime=200)


# ======= Motor control function =======
def servo_control_x():
    global current_angle_x, direction_x, running_x
    while running_x:
        if direction_x != 0: 
            next_angle = current_angle_x + direction_x  
            if MIN_ANGLE <= next_angle <= MAX_ANGLE:
                current_angle_x = next_angle
                duty_cycle = 7.5 + (current_angle_x / 18.0)
                pwm_x.ChangeDutyCycle(duty_cycle)
            else:
                direction_x = 0 
            time.sleep(0.1) 
        else:
            time.sleep(0.1) 

def servo_control_y():
    global current_angle_y, direction_y, running_y
    while running_y:
        if direction_y != 0: 
            next_angle = current_angle_y + direction_y  
            if MIN_ANGLE <= next_angle <= MAX_ANGLE:
                current_angle_y = next_angle
                duty_cycle = 7.5 + (current_angle_y / 18.0)
                pwm_y.ChangeDutyCycle(duty_cycle)
            else:
                direction_y = 0 
            time.sleep(0.1)  
        else:
            time.sleep(0.1) 


# =======================================
def user_input():
    global direction_x, direction_y, running_x, running_y, object_detect, END_FLAG, start_time
    
    try:
        while running_x and running_y:
            
            current_time = datetime.now()

            if (current_time - start_time) > timedelta(seconds=10):
                END_FLAG = 1


            if END_FLAG == 1:
                print("Exition program...")
                running_x = False
                running_y = False
                object_detect = False
                break


            if GPIO.input(communication_pin_x_1) == 0:
                if GPIO.input(communication_pin_x_0) == 0:
                    direction_x = 0
                else:
                    direction_x = 1
            else:
                if GPIO.input(communication_pin_x_0) == 0:
                    direction_x = -1
                else:
                    direction_x = 0


            if GPIO.input(communication_pin_y_1) == 0:
                if GPIO.input(communication_pin_y_0) == 0:
                    direction_y = 0
                else:
                    direction_y = 1
            else:
                if GPIO.input(communication_pin_y_0) == 0:
                    direction_y = -1
                else:
                    direction_y = 0


            if GPIO.input(communication_pin_x_0) and GPIO.input(communication_pin_x_1) and GPIO.input(communication_pin_y_0) and GPIO.input(communication_pin_y_1):
                object_detect = False
            else:
                object_detect = True


    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting program...")
        running_x = False
        running_y = False
        object_detect = False


# ======= Function to reset motor to center position =======
def return_to_center_x():
    global current_angle_x
    
    print_log('info', "Returning to center position...")

    while current_angle_x != 0:
        if current_angle_x > 0:
            current_angle_x -= 1
        elif current_angle_x < 0:
            current_angle_x += 1
        duty_cycle = 7.5 + (current_angle_x / 18.0)
        pwm_x.ChangeDutyCycle(duty_cycle)
        time.sleep(0.02) 
    
    print_log('info', "Servo returned to center.")

def return_to_center_y():
    global current_angle_y
    
    print_log('info', "Returning to center position...")

    while current_angle_y != 0:
        if current_angle_y > 0:
            current_angle_y -= 1
        elif current_angle_y < 0:
            current_angle_y += 1
        duty_cycle = 7.5 + (current_angle_y / 18.0)
        pwm_y.ChangeDutyCycle(duty_cycle)
        time.sleep(0.02) 
    
    print_log('info', "Servo returned to center.")


# ======= GPIO cleanup function =======
def cleanup():
    print_log('info', "Gpio pins clear ...")
    return_to_center_x()  
    return_to_center_y()
    pwm_x.stop()
    pwm_y.stop()
    GPIO.cleanup(servo_pin_x)
    GPIO.cleanup(servo_pin_y)
    GPIO.cleanup(input_pin_btn)
    GPIO.cleanup(communication_pin_x_0)
    GPIO.cleanup(communication_pin_x_1)
    GPIO.cleanup(communication_pin_y_0)
    GPIO.cleanup(communication_pin_y_1)
    print_log('info', "GPIO pins cleared.")
    

def print_log(status, message):
    if status == 'active':
        print('-------------------------------')
        print(Fore.GREEN + str(message) + Fore.RESET)
        print('-------------------------------')
        
    elif status == 'error':
        print('-------------------------------')
        print(Fore.RED + str(message) + Fore.RESET)
        print('-------------------------------')

    elif status == 'info':
        print('-------------------------------')
        print(Fore.BLUE + str(message) + Fore.RESET)
        print('-------------------------------')



# server kill
def stop_server():
    print_log('active', 'shutting server down!')
    cleanup()
    os.kill(os.getpid(), signal.SIGTERM)



if __name__ == '__main__':
    
    print_log('active', "PWM is fixed to 7.5")
    servo_x_thread = threading.Thread(target=servo_control_x, daemon=True)
    servo_x_thread.start()
    print_log('active', "servo x is started") 
    servo_y_thread = threading.Thread(target=servo_control_y, daemon=True)
    servo_y_thread.start()
    print_log('active', "servo y is started") 

    try:
        user_input()            
    
    finally:
        time.sleep(1)
        print_log('active', 'shutting server down!')
        cleanup()

