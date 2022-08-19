import serial
import time

import os
import sys

import json
import ast
import hashlib
import urllib.request
import urllib.parse
import boto3
import datetime
import glob

from collections import OrderedDict

import logging

global take_picture

# port1 = "/dev/ttyUSB0"
port1 = "/dev/ttyACM0"
port2 = "/dev/ttyACM1"
budRate = 9600

#initialise pygame
width = 1280
height = 960




try:
	BAY1 = serial.Serial(port1,budRate)
	BAY1.flushInput()
except Exception as e:
	print("Serial COM1 start error")
	print(e)
'''
try:
        BAY2 = serial.Serial(port2,budRate)
 	BAY2.flushInput()
except Exception as e:
	logger.exception("Serial COM2 start error")
	logger.exception(e)
'''

# CORDINATES_BAY1 = ["005037","204040","399047","598051","798060","808460","608453",\
# "409448","215443","010438","005842","205849","403850","603860","803866"]

CORDINATES_BAY1 = ["0150", "9950", "9901"]

CORDINATES_BAY2 = ["010032","209035","409039","610043","810045","805451","605445",\
"405442","209438","008436","013844","213847","406850","607855","803859"]


# side is serial commnuocation
# pic_side is, either BAY1 or BAY2
def move_cam(cordinates,side):

	try:

		phy_cord = cordinates

		cordinates_encode = cordinates.encode()

		side.write(cordinates_encode)

		time.sleep(1)
		side.flushInput()

		while True:

		# Get the number of bytes in the input buffer
			if side.inWaiting() > 0:
				take_picture = False
				incoming_data_raw = side.readline()
				incoming_data = str(incoming_data_raw, 'utf-8')

				# print("Received Ic", incoming_data)

				# ACK Cordinate length from Arduino is not always constant.  It requires 6 digits(as of 2019-08-02) cordinate to move the cam,
				# but the ACK cordinate doesnt have leading zeros.
				if len(incoming_data) == 8:							# cordinate with aditional two characters
					incoming_data = incoming_data[:6]
				elif len(incoming_data) == 7:
					incoming_data = incoming_data[:5]
				elif len(incoming_data) == 6:
					incoming_data = incoming_data[:4]

				# print("PArsed IC", incoming_data)
				# print("cordinates", cordinates)

				# Triming the cordinate sent to motor-controller to varify with the ACK cordinate
				if cordinates[:2] == '00':
					cordinates = cordinates[2:]
				elif cordinates[:1] == '0':
					cordinates = cordinates[1:]

				# print("Parsed cordinates", cordinates)

				if cordinates == incoming_data:
					# print("--------- CAN Take Picture ---------")
					take_picture = True

				elif incoming_data == "Home":
					logger.info("********** Came home, LimSwitch triggered ***************")
				else:
					take_picture = False
					logger.debug("Error in ACK")

				break

	except KeyboardInterrupt:
		sys.exit()
		side.flushInput()

	except Exception as e:
		print("Camera Movement or taking Picture Exception")


# move the camera back to Origin
def moveCamOrigin(side):
	cordinates = '9999'
	cordinates_encode = cordinates.encode()
	side.write(cordinates_encode)
	time.sleep(1)
	side.flushInput()
	print("Camera came to Origin")


while True:

	try:
		# cordinate_bay1 = input("Enter Cordinates: ")
		moveCamOrigin(BAY1)
		move_cam(CORDINATES_BAY1,BAY1)
		print("Camera Moved to location", CORDINATES_BAY1)

	except (KeyboardInterrupt, SystemExit):
		moveCamOrigin(BAY1)
		raise
