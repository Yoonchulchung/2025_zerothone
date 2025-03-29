#!/usr/bin/python3

import lgpio
import time

# GPIO setup
GPIO_PIN = 21 
PWM_FREQUENCY = 50 

# Servo configuration
MIN_DUTY = 2.5 
MAX_DUTY = 12.5  
ANGLE_RANGE = 180.0

# Open GPIO chip
chip = lgpio.gpiochip_open(0) 
lgpio.gpio_claim_output(chip, GPIO_PIN) 

# Function to calculate duty cycle for a given angle
def angle_to_duty_cycle(angle):
    return MIN_DUTY + (angle / ANGLE_RANGE) * (MAX_DUTY - MIN_DUTY)

# Gradual rotation from current to target angle
def rotate_servo(current_angle, target_angle, sleep_time):
    step = 1 if target_angle > current_angle else -1 
    for angle in range(current_angle, target_angle + step, step):
        duty_cycle = angle_to_duty_cycle(angle)
        lgpio.tx_pwm(chip, GPIO_PIN, PWM_FREQUENCY, duty_cycle)
        time.sleep(sleep_time)

# Main execution
try:
    # Configuration
    target_angle = 125 
    sleep_time = 0.015  
    
    print("Starting servo movement...")
    rotate_servo(target_angle, 0, sleep_time)
    print("Servo reached the 0.")

except KeyboardInterrupt:
    print("Program interrupted.")

finally:
    # Cleanup
    time.sleep(1)
    lgpio.tx_pwm(chip, GPIO_PIN, 0, 0) 
    lgpio.gpio_free(chip, GPIO_PIN) 
    print("GPIO cleanup complete.")

