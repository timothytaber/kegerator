# Kegerator
# 2018.05.03

import time

import RPi.GPIO as GPIO

import Adafruit_DHT
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import json

TOWER_PIN = 23
BASE_PIN = 24
FAN_PIN = 8
COMPRESSOR_PIN = 25

compressorOn = False
fanOn = False

# Set temperature sensors to Adafruit_DHT.AM2302
sensor = Adafruit_DHT.AM2302

# Initialize relay GPIO pins & set to low:
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(COMPRESSOR_PIN, GPIO.OUT)
GPIO.output(FAN_PIN, GPIO.LOW)
GPIO.output(COMPRESSOR_PIN, GPIO.LOW)

# Initialize 128x64 OLED display with hardware I2C:
RST = None
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

def refreshScreen():

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Write two lines of text.
    draw.text((x, top), "Base = {0:0.1f}F".format(baseTemp), font=font, fill=255)
    draw.text((x, top+8), "Tower = {0:0.1f}F".format(towerTemp), font=font, fill=255)
    draw.text((x, top+16), "Now pouring: {}".format(onTap), font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)

def updateJson():
    cfg = open('config.json', 'r')
    config = json.load(cfg)
    cfg.close()
    return config

def getTemp(pin):
    """Uses Adafruit_DHT library to read from temperature sensors"""
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    humidity, celcius = Adafruit_DHT.read_retry(sensor, pin)
    fahrenheit = celcius * 1.8 + 32
    return fahrenheit

def checkFan(on, tower, base, setDelta):
    currentDelta = tower - base
    if on:
        if currentDelta <= 0:
            GPIO.output(FAN_PIN, GPIO.LOW)
            return False
        else:
            GPIO.output(FAN_PIN, GPIO.HIGH)
            return True
    else:
        if currentDelta >= setDelta:
            GPIO.output(FAN_PIN, GPIO.HIGH)
            return True
        else:
            GPIO.output(FAN_PIN, GPIO.LOW)
            return False

def checkCompressor(on, base, max, min):
    if on:
        if base <= min:
            GPIO.output(COMPRESSOR_PIN, GPIO.LOW)
            return False
        else:
            GPIO.output(COMPRESSOR_PIN, GPIO.HIGH)
            return True
    else:
        if base >= max:
            GPIO.output(COMPRESSOR_PIN, GPIO.HIGH)
            return True
        else:
            GPIO.output(COMPRESSOR_PIN, GPIO.LOW)
            return False

try:
    while True:
        fromConfig = updateJson()
        onTap = fromConfig['ON_TAP']
        idealTemp = fromConfig['TEMPS']['IDEAL']
        plusMinus = fromConfig['TEMPS']['PLUS_MINUS']
        maxTemp = idealTemp + plusMinus
        minTemp = idealTemp - plusMinus
        baseTemp = getTemp(BASE_PIN)
        towerTemp = getTemp(TOWER_PIN)
        fanOn = checkFan(fanOn, towerTemp, baseTemp, plusMinus)
        compressorOn = checkCompressor(compressorOn, baseTemp, maxTemp, minTemp)
        refreshScreen()

except KeyboardInterrupt:
    print "Quit"
    GPIO.cleanup()
