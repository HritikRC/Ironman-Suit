import time
import math
import RPi.GPIO as GPIO
from mpu6050 import mpu6050
from espeak import espeak as jarvis
mpu = mpu6050(0x68)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(18, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

lid = GPIO.PWM(18, 50) # 11 is a pin. 50 = 50Hz
shoot = GPIO.PWM(15, 50)

lid.start(0) # pulse off (0)
shoot.start(0) # pulse off (0)

mode = "close" # open/close
count = 0
latestFlick = 0
iterations = 0
while True:
    if mpu.get_gyro_data()["x"] < -120:
        if iterations - latestFlick < 10:
            count = count + 1
            jarvis.synth(str(count))
            print(count)
        else:
            count = 0
        latestFlick = iterations
    
    if count == 5:
        count = 0
        print("Initiating arm weapon system")
        time.sleep(0.5)

        if mode == "close":
            jarvis.synth("Opening missile launcher")
            lid.ChangeDutyCycle(2 + (90 / 18))
            time.sleep(0.5)
            lid.ChangeDutyCycle(0)

            time.sleep(0.5)
            
            shoot.ChangeDutyCycle(2 + (80 / 18))
            time.sleep(0.5)
            shoot.ChangeDutyCycle(0)
            
            mode = "open"
        elif mode == "open":
            jarvis.synth("Closing missile launcher")
            shoot.ChangeDutyCycle(2 + (0 / 18))
            time.sleep(0.5)
            shoot.ChangeDutyCycle(0)

            time.sleep(0.5)

            lid.ChangeDutyCycle(2 + (0 / 18))
            time.sleep(0.5)
            lid.ChangeDutyCycle(0)

            mode = "close"
    iterations = iterations + 1 
    time.sleep(0.1)
