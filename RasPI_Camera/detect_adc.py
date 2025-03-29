####################################
# Project : Zerothone Dankook Univ.
# Created : Yoonchul Chung
# Date    : 2025.03.29
####################################
import spidev
import RPi.GPIO as GPIO
import time

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
        print(Fore.GREEN + "[ADC]    " + str(kst_time) + " : " + str(message) + Fore.RESET)
        
    elif status == 'error':
        print(Fore.RED + "[ADC]    " + str(kst_time) + " : " + str(message) + Fore.RESET)

    elif status == 'info':
        print(Fore.BLUE + "[ADC]    " + str(kst_time) + " : " + str(message) + Fore.RESET)



########################################################################
CS_MCP3208  = 25  
SPI_CHANNEL = 0
SPI_SPEED   = 1000000  # 1MHz

LED_PIN = 13  

def read_mcp3208_adc(adc_channel):

    buff = [0x06 | ((adc_channel & 0x07) >> 2), 
            (adc_channel & 0x07) << 6, 
            0x00]

    GPIO.output(CS_MCP3208, GPIO.LOW) 
    adc = spi.xfer2(buff)
    GPIO.output(CS_MCP3208, GPIO.HIGH)
    adc_value = ((adc[1] & 0x0F) << 8) | adc[2] # 0~4095
    return adc_value  


########################################################
# Main
########################################################
def main():
    adc_channel_light = 0

    # =================== Init GPIO ======================
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CS_MCP3208, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(LED_PIN, GPIO.OUT)

    pwm = GPIO.PWM(LED_PIN, 1000)  # SET PWM 1kHz
    pwm.start(100)                 # Init to 100
    
    global spi
    spi = spidev.SpiDev()
    spi.open(0, SPI_CHANNEL)  # SPI Bus 0, Channel 0
    spi.max_speed_hz = SPI_SPEED

    try:
        while True:
            ########################################################
            # Read ADC
            ########################################################
            adc_value_light = read_mcp3208_adc(adc_channel_light)

            if adc_value_light <= 1200:
                duty_cycle = 100
            elif adc_value_light >= 3100:
                duty_cycle = 0 
            else:
                duty_cycle = ((3100 - adc_value_light) / (3100 - 1200)) * 100
                duty_cycle = max(0, min(100, duty_cycle))


            ########################################################
            # Change LED Light
            ########################################################
            pwm.ChangeDutyCycle(duty_cycle)
            print_log('active', f"Light sensor = {adc_value_light} | LED Duty : {duty_cycle:.2f}%")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print_log('info', "Closing...")
    finally:
        print_log('info', "Closing...")
        pwm.ChangeDutyCycle(0)
        pwm.stop()     
        spi.close()     
        GPIO.cleanup()  




if __name__ == "__main__":
    try:
        main()
    finally:
        GPIO.cleanup()
