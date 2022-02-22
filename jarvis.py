import time
from espeak import espeak as jarvis
import datetime
import speech_recognition as sr
import RPi.GPIO as GPIO

print("Starting Jarvis...")

GPIO.setmode(GPIO.BOARD)
r = sr.Recognizer()
r.pause_threshold = 2 # 2 seconds pause time before phrase is sent to API

led1 = 7
led2 = 12
GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.output(led1, False)
GPIO.output(led2, False)

trigger = 32
echo = 11
GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.output(trigger, False)

GPIO.setup(18, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
lid = GPIO.PWM(18, 50) # 11 is a pin. 50 = 50Hz
shoot = GPIO.PWM(15, 50)
lid.start(0) # pulse off (0)
shoot.start(0) # pulse off (0)
mode = "close" # open/close

# Initiating JARVIS
dateinfo = datetime.datetime.now()
if dateinfo.hour <= 12:
    jarvis.synth("Good morning")
    print("1")
elif dateinfo.hour > 12 and dateinfo.hour < 17:
    jarvis.synth("Good afternoon")
    print("1")
elif dateinfo.hour >= 17:
    jarvis.synth("Good evening")
    print("1")

eyesOnCommands = ["switch on LED eyes", "switch on eyes", "turn on LED eyes", "turn on eyes", "turn on ice"]
eyesOffCommands = ["switch off LED eyes", "switch off eyes", "turn off LED eyes", "turn off eyes", "turn off ice"]
ultrasonicCommands = ["is there something behind me", "initiate ultrasonic sensor", "give me a distance from the ultrasonic sensor", "shoot the ultrasonic waves", "shoot ultrasonic waves"]
missileOnCommands = ["Jarvis open missile launcher", "Jervis open missile launcher", "bring the missile launcher up", "bring up the missile launcher", "initiate missile launcher", "initiate the missile launcher", "open the missile launcher", "open missile launcher"]
missileOffCommands = ["bring the missile launcher down", "bring down the missile launcher", "Close missile launcher", "Close the missile launcher"]
distance = 0
while True:
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            voice_data = r.recognize_google(audio)
            print(voice_data)
            if voice_data in eyesOnCommands:
                jarvis.synth("Turning on eyes")
                GPIO.output(led1, True)
                GPIO.output(led2, True)
            if voice_data in eyesOffCommands:
                jarvis.synth("Turning off eyes")
                GPIO.output(led1, False)
                GPIO.output(led2, False)
            if voice_data in ultrasonicCommands:
                jarvis.synth("Shooting ultrasonic waves")
                GPIO.output(trigger, True)
                time.sleep(0.00001)
                GPIO.output(trigger, False)
                starttime = 0
                endtime = 0
                while GPIO.input(echo) == 0:
                    starttime = time.time()
                while GPIO.input(echo) == 1:
                    endtime = time.time()
                duration = endtime - starttime
                distance = duration * 17150
                jarvis.synth("The distance to the object is " + str(format(distance, ".0f")) + " centimeters")
            if voice_data in missileOnCommands:
                if mode == "close":
                    jarvis.synth("Opening the missile launcher")
                    lid.ChangeDutyCycle(2 + (90 / 18))
                    time.sleep(0.5)
                    lid.ChangeDutyCycle(0)
                    time.sleep(0.5)
                    shoot.ChangeDutyCycle(2 + (80 / 18))
                    time.sleep(0.5)
                    shoot.ChangeDutyCycle(0)
                    mode = "open"
                else:
                    jarvis.synth("The missile launcher is already open")
            if voice_data in missileOffCommands:
                if mode == "open":
                    jarvis.synth("Closing the missile launcher")
                    shoot.ChangeDutyCycle(2 + (0 / 18))
                    time.sleep(0.5)
                    shoot.ChangeDutyCycle(0)
                    time.sleep(0.5)
                    lid.ChangeDutyCycle(2 + (0 / 18))
                    time.sleep(0.5)
                    lid.ChangeDutyCycle(0)
                    mode = "close"
                else:
                    jarvis.synth("The missile launcher is already closed")
            if voice_data == "good afternoon" or voice_data == "good evening" or voice_data == "good morning":
                dateinfo = datetime.datetime.now()
                if dateinfo.hour <= 12:
                    jarvis.synth("Good morning")
                    print("1")
                elif dateinfo.hour > 12 and dateinfo.hour < 17:
                    jarvis.synth("Good afternoon")
                    print("1")
                elif dateinfo.hour >= 17:
                    jarvis.synth("Good evening")
                    print("1")
        except sr.UnknownValueError:
            print("Did not get that...")
        except sr.RequestError:
            jarvis.synth("Service down...")
