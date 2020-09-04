#!/usr/bin/python3

import os
import sys
import signal
import getopt
import time
import RPi.GPIO as GPIO

TRIG = 16
ECHO = 18

'''
To setup the hardware use a raspberry pi and either a HY-SRF05 or a HC-SR04.
Connect the SR-module to the raspberry pi in this way:

-----------------------------------------Edge of pi (furthest from you)--------------------------------------

       VCC       GND                      TRG  ECH
        |         |                        |    |
   +----v---------v------------------------v----v-----------------------------------------------------------+
   |    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    |
   |    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    x    |
   +--------------------------------------------------------------------------------------------------------+

-----------------------------------------Front of Pi (closest to you)----------------------------------------

IMPORTANT: You must also connect resistors between ECH <-> GND [470 ohm] and ECH <-> cable [330 ohm] like so:

   ECH                    GND
    |                      |
    *--[330]---*---[470]---*
               |           |
             GPIO24       GND

'''

def exit_gracefully(sig, frame):
	GPIO.cleanup()
	sys.exit(0)

def setup():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.output(TRIG,0)

	GPIO.setup(ECHO,GPIO.IN)

	time.sleep(0.1)

def start(freq = 25.0):
	timeout = (1.0 / freq)
	initial = time.time()

	signal.signal(signal.SIGINT, exit_gracefully)
	while True:

		GPIO.output(TRIG,1)
		time.sleep(0.0001)
		GPIO.output(TRIG,0)

		while GPIO.input(ECHO) == 0:
			pass
		start = time.time()

		while GPIO.input(ECHO) == 1:
			pass
		stop = time.time()

		print('{:f};{:f}'.format((stop - initial), (stop - start) * (34029 / 2)), file=sys.stdout)
		time.sleep(timeout)

def usage(code = 0):
	filename = os.path.basename(__file__)
	print(filename + ' -f <frequency>', file=sys.stderr)
	print('\nReads distance at a rate based on (-f) frequency and prints <time>;<distance> to stdout.', file=sys.stderr)
	print('The operation of measurement is ended using SIGINT or Ctrl+C.', file=sys.stderr)
	print('\nThis tool is intended for a raspberry pi using a HY-SRF05 or a HC-SR04.', file=sys.stderr)
	print('Default pins used are GPIO23 (trig) and GPIO24 (echo).', file=sys.stderr)
	print('\nUsage:\n  ' + filename + ' [options...]', file=sys.stderr)
	print('  ' + filename + ' -f 30 > output.csv', file=sys.stderr)
	print('\nOptions:', file=sys.stderr)
	print('  -f, --frequency            determines read frequency. Default is 25hz', file=sys.stderr)
	print('\nReport bugs to <chris@noxz.tech>', file=sys.stderr)
	print('Source code: https://git.noxz.tech/srfinder', file=sys.stderr)
	sys.exit(code)

def main(argv):
	freq = 25.0
	try:
		opts, args = getopt.getopt(argv,"hf:",["frequency="])
	except getopt.GetoptError:
		usage(2)
	for opt, arg in opts:
		if opt == '-h':
			usage(0)
		elif opt in ("-f", "--frequency"):
			freq = float(arg)
	if (freq > 0.0 and freq < 100.0):
		setup()
		start(freq)

if __name__ == "__main__":
	main(sys.argv[1:])
