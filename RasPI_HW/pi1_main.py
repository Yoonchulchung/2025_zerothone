#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import os
from table_mode import read_table_mode, write_table_mode


# file_name
file_table_setting = "./table_setting.py"
file_table_initial = "./table_initial.py"
file_AI_tracking = "./AI_tracking.py"

# GPIO 핀 설정
input_pin_btn = 26
input_pin_dis = 19

output_pin_pi2 = 5

# GPIO 초기화
GPIO.setmode(GPIO.BCM)

GPIO.setup(input_pin_btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(input_pin_dis, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(output_pin_pi2, GPIO.OUT, initial=GPIO.LOW)


# 인터럽트 발생 시 실행될 콜백 함수
def ISR_btn(channel):
    print("btn detected on pin:", channel)
    if read_table_mode(1) == "initial" and GPIO.input(input_pin_dis) and read_table_mode(2) == "btn_off":
        GPIO.output(output_pin_pi2, GPIO.HIGH)
        os.system(file_AI_tracking)
        GPIO.output(output_pin_pi2, GPIO.LOW)
    
    elif read_table_mode(1) == "setting" and GPIO.input(input_pin_dis) and read_table_mode(2) == "btn_off":
        os.system(file_table_initial)
    
    elif read_table_mode(2) == "btn_on":
        write_table_mode(2, "btn_off")

def ISR_dis(channel):
    print("Rising edge detected on pin:", channel)
    if GPIO.input(channel) and read_table_mode(1) == "initial": 
        GPIO.output(output_pin_pi2, GPIO.HIGH)
        os.system(file_AI_tracking)
        GPIO.output(output_pin_pi2, GPIO.LOW)
    
    else: 
        print("Lower edge detected on pin:", channel)
        if read_table_mode(1) == "setting":
            os.system(file_table_initial)


# 인터럽트 설정 (HIGH 엣지)
GPIO.add_event_detect(input_pin_btn, GPIO.RISING, callback=ISR_btn, bouncetime=200)
GPIO.add_event_detect(input_pin_dis, GPIO.BOTH, callback=ISR_dis, bouncetime=200)


if __name__ == "__main__":
    
    try:
        print("Waiting for interrupt... Press Ctrl+C to exit.")
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        time.sleep(1)
        GPIO.cleanup(input_pin_btn)
        GPIO.cleanup(input_pin_dis)
        GPIO.cleanup(output_pin_pi2)
        print("GPIO cleanup complete.")

