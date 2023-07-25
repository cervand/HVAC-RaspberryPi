#libraries used for this project
import RPi.GPIO as GPIO
import time
import I2C_LCD_driver
import Adafruit_DHT
from math import trunc
sensor = Adafruit_DHT.DHT11


#global vars
lightStatus = "ON"
hvacStatus = "OFF"
curTemp = 00
desiredTemp = 75
doorWinOpen = "SAFE"
time_a=time.time()
alreadyDisplayed = False
preHVACState = "OFF"

heatMode = False
offMode = False
acMode = False


#PIN ASSIGNMENT,constant variables used for easier reference of other  functions------------------------
#lcd
mylcd = I2C_LCD_driver.lcd()

#buttons
rBut = 17
bBut = 24
doorWinBut = 26

#leds
gLed = 23
rLed = 4
bLed = 18

#sensors
dht = 25
pir = 21

#SETUP ---------------------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#led setup
GPIO.setup(gLed, GPIO.OUT)
GPIO.setup(rLed, GPIO.OUT)
GPIO.setup(bLed, GPIO.OUT)

#button setup, I used pull down to act as a more intuitive button
GPIO.setup(rBut, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bBut, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bBut, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(doorWinBut, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#semsor setup
GPIO.setup(pir, GPIO.IN)



def UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus):
    curTempStr = str(curTemp)
    desiredTempStr = str(desiredTemp)
    mylcd.lcd_display_string(curTempStr + "/" + desiredTempStr + "    D:" + doorWinOpen, 1)
    mylcd.lcd_display_string("H:" + hvacStatus + "     L:" + lightStatus, 2)

def AmbientLightController():
    global lightStatus
    global time_a
    
    if(GPIO.input(pir) == 1):
        GPIO.output(gLed,True)
        time_a=time.time()
        lightStatus = "ON "
        print("movement detected")
        UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus)
    elif(GPIO.input(pir) == 0 and (time.time()-time_a) > 10):
        GPIO.output(gLed, False)
        lightStatus = "OFF"
        UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus)
            
def HVACController():
    global doorWinOpen
    global curTemp
    global desiredTemp
    global hvacStatus
    global preHVACState
    
    global heatMode
    global acMode
    global offMode
    print("I am running")
    global alreadyDisplayed
    humidity, temperature = Adafruit_DHT.read(sensor, dht)
    

        
    if(GPIO.input(rBut) == 0):
        desiredTemp = desiredTemp + 1
        UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus)
        print("I changed it")            
    elif(GPIO.input(bBut) == 0):
        desiredTemp = desiredTemp -1
        UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus)
        
    if temperature is not None:
        curTemp =trunc((temperature*(1.8))+32)
    
    if(doorWinOpen == "OPEN"):
        GPIO.output(rLed, False)
        GPIO.output(bLed, False)

        heatMode = False
        acMode = False
        offMode = False

        hvacStatus = "HALT"
    elif(curTemp < desiredTemp-3 and not heatMode):
        heatMode = True
        acMode = False
        offMode = False
        GPIO.output(rLed, True)
        GPIO.output(bLed, False)
        
        mylcd.lcd_clear()
        mylcd.lcd_display_string("HEATER ENABLED",1)
        time.sleep(3)
        mylcd.lcd_clear()
        
        hvacStatus = "HEAT"
        UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus)
    elif(curTemp > desiredTemp+3 and not acMode):
        heatMode = False
        acMode = True
        offMode = False
        GPIO.output(bLed, True)
        GPIO.output(rLed, False)
        
        mylcd.lcd_clear()
        mylcd.lcd_display_string("AC ENABLED",1)
        time.sleep(3)
        mylcd.lcd_clear()
        
        hvacStatus = "AC  "
        UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus)
    elif(not offMode and curTemp <= desiredTemp+3 and curTemp >= desiredTemp-3):
        
        heatMode = False
        acMode = False
        offMode = True
        
        GPIO.output(rLed, False)
        GPIO.output(bLed, False)
        hvacStatus = "OFF "
        
        mylcd.lcd_clear()
        mylcd.lcd_display_string("AC/HEATER OFF",1)
        time.sleep(3)
        mylcd.lcd_clear()
        
        UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus)

def SecurityController():
    global doorWinOpen
    global hvacStatus
    global preHVACState
    
    if(GPIO.input(doorWinBut) == 0):
        if(doorWinOpen == "OPEN"): doorWinOpen = "SAFE"
        else: doorWinOpen = "OPEN"
        mylcd.lcd_clear()
        mylcd.lcd_display_string("DOOR/WINDOW " + doorWinOpen, 1)
        if(doorWinOpen == "OPEN"): mylcd.lcd_display_string("HVAC OFF", 2)
        else:
            mylcd.lcd_display_string("HVAC ON", 2)
            #hvacStatus = preHVACState
        time.sleep(5)
        mylcd.lcd_clear()
        UpdateLCD(curTemp, desiredTemp, doorWinOpen, hvacStatus, lightStatus)
    
    

while(True):
    HVACController()
    AmbientLightController()
    SecurityController()

