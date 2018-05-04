# Kegerator
# 2018.05.03

import time

import RPi.GPIO as GPIO

import Adafruit_DHT
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.AM2302

towerPin = 23
basePin = 24
fanPin = 8
compressorPin = 25

towerTemp = 0
baseTemp = 0
idealTemp = 40
plusMinus = 2
maxTemp = idealTemp + plusMinus
minTemp = idealTemp - plusMinus
compressorOn = False
fanOn = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(fanPin, GPIO.OUT)
GPIO.setup(compressorPin, GPIO.OUT)
GPIO.output(fanPin, GPIO.HIGH)
GPIO.output(compressorPin, GPIO.HIGH)

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

    draw.text((x, top),       "Base={0:0.1f}F".format(baseTemp), font=font, fill=255)
    draw.text((x, top+8),     "Tower={0:0.1f}F".format(towerTemp), font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)

def checkTemps():
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    towerHum, towerCels = Adafruit_DHT.read_retry(sensor, towerPin)
    baseHum, baseCels = Adafruit_DHT.read_retry(sensor, basePin)

    global towerTemp
    global baseTemp
    towerTemp = towerCels * 1.8 + 32
    baseTemp = baseCels * 1.8 + 32

def checkFan():
    global fanOn
    deltaTemp = towerTemp - baseTemp
    if fanOn:
        if deltaTemp <= plusMinus * -1:
            GPIO.output(fanPin, GPIO.HIGH)
            fanOn = False
        else:
            GPIO.output(fanPin, GPIO.LOW)
    else:
        if deltaTemp >= plusMinus:
            GPIO.output(fanPin, GPIO.LOW)
            fanOn = True
        else:
            GPIO.output(fanPin, GPIO.HIGH)

try:
    while True:
        checkTemps()
        checkFan()
        refreshScreen()

except KeyboardInterrupt:
    print "Quit"
    GPIO.cleanup()
