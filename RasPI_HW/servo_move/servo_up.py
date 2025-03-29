#!/usr/bin/python3

import lgpio
import time
import threading


# GPIO setup
GPIO_PIN1 = 16  
GPIO_PIN2 = 20
PWM_FREQUENCY = 50  


# Servo configuration
MIN_DUTY = 2.5  
MAX_DUTY = 12.5 
ANGLE_RANGE = 180.0


# Open GPIO chip
chip = lgpio.gpiochip_open(0) 
lgpio.gpio_claim_output(chip, GPIO_PIN1) 
lgpio.gpio_claim_output(chip, GPIO_PIN2)


# Function to calculate duty cycle for a given angle
def angle_to_duty_cycle1(angle):
    return MIN_DUTY + (angle / ANGLE_RANGE) * (MAX_DUTY - MIN_DUTY)

def angle_to_duty_cycle2(angle):
    return MIN_DUTY + (angle / ANGLE_RANGE) * (MAX_DUTY - MIN_DUTY)


# Gradual rotation from current to target angle
def rotate_servo1(current_angle, target_angle, sleep_time):
    step = 1 if target_angle > current_angle else -1 
    for angle in range(current_angle, target_angle + step, step):
        duty_cycle = angle_to_duty_cycle1(angle)
        lgpio.tx_pwm(chip, GPIO_PIN1, PWM_FREQUENCY, duty_cycle)
        time.sleep(sleep_time) 

def rotate_servo2(current_angle, target_angle, sleep_time):
    step = 1 if target_angle > current_angle else -1 
    for angle in range(current_angle, target_angle + step, step):
        duty_cycle = angle_to_duty_cycle2(angle)
        lgpio.tx_pwm(chip, GPIO_PIN2, PWM_FREQUENCY, duty_cycle)
        time.sleep(sleep_time) 


# Thread function for Servo
def servo1_thread():
    try:
        print("Servo 1 starting...")
        rotate_servo1(0, 90, 0.015) 
        print("Servo 1 completed.")
    except Exception as e:
        print(f"Servo 1 error: {e}")

def servo2_thread():
    try:
        print("Servo 2 starting...")
        rotate_servo2(90, 0, 0.015)
        print("Servo 2 completed.")
    except Exception as e:
        print(f"Servo 2 error: {e}")


# Main execution
try:
    # Thread create
    thread1 = threading.Thread(target=servo1_thread)
    thread2 = threading.Thread(target=servo2_thread)

    # Thread start
    thread1.start()
    thread2.start()

    # Waiting Thread finish
    thread1.join()
    thread2.join()

    print("Both servos have completed their movements.")

except KeyboardInterrupt:
    print("Program interrupted.")

finally:
    # Cleanup
    time.sleep(1)
    lgpio.tx_pwm(chip, GPIO_PIN1, 0, 0)
    lgpio.tx_pwm(chip, GPIO_PIN2, 0, 0)  
    lgpio.gpio_free(chip, GPIO_PIN1)  
    lgpio.gpio_free(chip, GPIO_PIN2) 
    print("GPIO cleanup complete.")

