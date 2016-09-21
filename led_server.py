# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import socketio
import eventlet
import math
from flask import Flask, render_template

from neopixel import *
from socketIO_client import SocketIO, LoggingNamespace


# LED strip configuration:
LED_COUNT      = 180      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
REFRESH        = False

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel(((i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def on_rgb(*args):
	print(args)

	for i in range(LED_COUNT):
		strip.setPixelColorRGB(i, args[0]['g'],args[0]['r'],args[0]['b'])
	strip.show()

sio = socketio.Server()
app = Flask(__name__)

@app.route('/')
def index():
	"""Serve the client-side application."""
	return render_template('index.html')

@sio.on('rgb', namespace='/color')
def rgb(sid, data):
	REFRESH = True
	# print REFRESH

	for i in range(LED_COUNT ):
		strip.setPixelColorRGB(i, data['g'],data['r'],data['b'])
	strip.show()

# Convolve breathing animation
@sio.on('breathe', namespace='/color')
def breathe(sid, data):
	REFRESH = False
	delay = .018
	amplitude = LED_BRIGHTNESS / 2
	resolution = 500

	while (True):
		for i in range(resolution):
			if (REFRESH): return # Exit condition
			# print REFRESH

			delt = amplitude * math.cos(2 * math.pi * i / resolution)
			brights = LED_BRIGHTNESS + (int)( delt - amplitude )

			# strip.setBrightness( LED_BRIGHTNESS + (int)( delt - amplitude ) )
			if brights < 8:
				brights = 8

			strip.setBrightness( brights )
			strip.show()

			time.sleep(delay)

@sio.on('shift', namespace='/color')
# Slowly shift through whole color spectrum
def shift(sid, data):
	REFRESH = False
	delay = .05
	while (REFRESH != True):
		# Red to pink
		for i in range(0,256):
			if (REFRESH): return
			time.sleep(delay)
			for led_num in range(LED_COUNT ):
				strip.setPixelColorRGB(led_num, 255,0,i)
			strip.show()
		# Pink to blue
		for i in range(255,-1,-1):
			if (REFRESH): return
			time.sleep(delay)
			for led_num in range(LED_COUNT :
				strip.setPixelColorRGB(led_num, i,0,255)
			strip.show()
		# Blue to teal
		for i in range(0,256):
			if (REFRESH): return
			time.sleep(delay)
			for led_num in range(LED_COUNT ):
				strip.setPixelColorRGB(led_num, 0,i,255)
			strip.show()
		# Teal to green
		for i in range(256,0,-1):
			if (REFRESH): return
			time.sleep(delay)
			for led_num in range(LED_COUNT ):
				strip.setPixelColorRGB(led_num, 0,255,i)
			strip.show()
		# Green to yellow
		for i in range(0,256):
			if (REFRESH): return
			time.sleep(delay)
			for led_num in range(LED_COUNT ):
				strip.setPixelColorRGB(led_num, i,255,0)
			strip.show()
		# Yellow to red
		for i in range(256,0,-1):
			if (REFRESH): return
			time.sleep(delay)
			for led_num in range(LED_COUNT ):
				strip.setPixelColorRGB(led_num, 255,i,0)
			strip.show()


# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	global strip
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	strip.begin()

	#socketIO = SocketIO('localhost', 3000, LoggingNamespace)
	'''
	socketIO = SocketIO('192.168.1.148', 3000, LoggingNamespace)
	socketIO.on('rgb', on_rgb)
	socketIO.wait()
	'''

	# wrap Flask application with engineio's middleware
	app = socketio.Middleware(sio, app)

    	# deploy as an eventlet WSGI server
    	eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

	print ('Press Ctrl-C to quit.')
