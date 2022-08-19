import serial
import time
import datetime

import os
import pygame, sys

from pygame.locals import *
import pygame.camera

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

#Access IDs for AWS upload
ACCESS_ID = 'AKIAIRPU2BADUGM4MAXQ'
ACCESS_KEY = '40lFoFFB2rtBVqoygomIwrXVzNzl3AxhpQD0k7t4'

IMAGE_FILE_PATH = "/home/pi/Desktop/Images/*jpg"
LOG_FILE_PATH = "/home/pi/Desktop/LogFiles/*log"

# port1 = "/dev/ttyUSB0"
port1 = "/dev/ttyACM0"
port2 = "/dev/ttyACM1"
budRate = 9600

# Schedule of when pictures need to be taken
#
START_TIME = "08:00:00"
END_TIME = "17:00:00"


#initialise pygame

width = 1280
height = 960

pygame.init()
pygame.camera.init()


# Logg File Initilization
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)-8s:%(lineno)04d:%(name)s:%(message)s')

file_handler = logging.FileHandler('/home/pi/Desktop/LogFiles/_{:%Y-%m-%d--%H-%M-%S}_CamTakePic.log'.format(datetime.datetime.now()))
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info("Starting the Script")


try:
	cam0 = pygame.camera.Camera("/dev/video0",(width,height))
	cam0.start()
except Exception as e:
	logger.exception("Camera 1 is Not connected")
	logger.exception(e)


try:
	cam1 = pygame.camera.Camera("/dev/video2",(width,height))
	cam1.start()
except Exception as e:
	logger.exception("Camera 2 is Not connected")
	logger.exception(e)



try:
	BAY1 = serial.Serial(port1,budRate)
	BAY1.flushInput()
except Exception as e:
	logger.exception("Serial COM1 start error")
	logger.exception(e)


try:
	BAY2 = serial.Serial(port2,budRate)
	BAY2.flushInput()
except Exception as e:
	logger.exception("Serial COM2 start error")
	logger.exception(e)

# Camera's will move sequentially;
# can make it move simultaniously

# When updating this cordinates, Mainly when the significant fig of cordinate changes
# need to update "moveCamOrigin" cordinates as well

CORDINATES_BAY1 = ["005037","204040","399047","598051","798060","808460","608453",\
"409448","215443","010438","005842","205849","403850","603860","803866"]

CORDINATES_BAY2 = ["010032","209035","409039","610043","810045","805451","605445",\
"405442","209438","008436","013844","213847","406850","607855","803859"]

global resolution_sig_fig
global BAY1_FIRST_HOLE_CORDINATE
global BAY1_LAST_HOLE_CORDINATE
global BAY2_FIRST_HOLE_CORDINATE
global BAY2_LAST_HOLE_CORDINATE
number_of_holes = 9								# Number of Holes to place plants in the rack
number_of_racks = 3
resolution_sig_fig = 3 							# How many digits needs to specify one component of cartesian cordinate

# if we get the first and last cordinate from the CORDINATES_BAY list then,
# Its hard to calculate the distance between plant, racks; cz there will be a case where first and/or last hole may not have
# plants
BAY1_FIRST_HOLE_CORDINATE = "005037"
BAY1_LAST_HOLE_CORDINATE = "803866"
BAY2_FIRST_HOLE_CORDINATE = "010032"
BAY2_LAST_HOLE_CORDINATE = "803859"

def convert_cord_to_physical_cord(CORDINATE,first_plant_cordinate,last_plant_cordinate):
	min_x_axis = int(first_plant_cordinate[:resolution_sig_fig])
	min_y_axis = int(first_plant_cordinate[resolution_sig_fig:])
	max_x_axis = int(last_plant_cordinate[:resolution_sig_fig])
	max_y_axis = int(last_plant_cordinate[resolution_sig_fig:])

	dist_between_plants = ( max_x_axis - min_x_axis ) / (number_of_holes - 1)
	dist_between_racks = ( max_y_axis - min_y_axis ) / (number_of_racks - 1)

	x_cordinate = int(CORDINATE[:resolution_sig_fig])
	y_cordinate = int(CORDINATE[resolution_sig_fig:])

	col_ID = round( x_cordinate / dist_between_plants,0) + 1
	rack_ID = round( y_cordinate / dist_between_racks,0) + 1

	return(col_ID,rack_ID)

take_picture = False


## upload AWS image link to API
global aws_url_list
aws_url_list = []

camera_device_ID = 143

# side is serial commnuocation
# pic_side is, either BAY1 or BAY2
def move_cam(cordinates,side,cam,pic_side,ctr):
	BAY1_RACK_START_ID = 13				# if starting Rack_ID is 14, then this variable is assigned to be 14 - 1
	BAY2_RACK_START_ID = 16
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

		if take_picture:
			# print("Picture taken and saved; Hell YEAH!!!!")
			image = cam.get_image()
			itr = 0
			# to let the Camera to get correct frame. (Need to check if thats the case)
			# when taken once, the frame is not properly captured
			while itr < 8:
				image = cam.get_image()
				itr = itr + 1

			col = 0.0
			rack = 0.0
			if pic_side == "bay1":
				pic_side = "BAY1"
				col, rack = convert_cord_to_physical_cord(phy_cord, BAY1_FIRST_HOLE_CORDINATE, BAY1_LAST_HOLE_CORDINATE)
			elif pic_side == "bay2":
				pic_side = "BAY2"
				col, rack = convert_cord_to_physical_cord(phy_cord, BAY2_FIRST_HOLE_CORDINATE, BAY2_LAST_HOLE_CORDINATE)

			plant_image_name = str(pic_side)+ '_{:02d}-{:02d}'.format(int(col),int(rack)) + '_{:%Y-%m-%d--%H-%M-%S}'.format(datetime.datetime.now()) +'.jpg'

			pygame.image.save(image,'Images/'+'_'+ plant_image_name )

			aws_image_url = "https://aigrow-box.s3.amazonaws.com/plant_images/Images/" + plant_image_name
			if pic_side == "BAY1":
				aws_url_list.append( OrderedDict( [('rackID',str(int(rack) + BAY1_RACK_START_ID)) , ('columnID',str(int(col))), ('image_url', aws_image_url) ] ) )

			elif pic_side == "BAY2" :
				aws_url_list.append( OrderedDict( [('rackID',str(int(rack) + BAY2_RACK_START_ID)) , ('columnID',str(int(col))), ('image_url', aws_image_url) ] ) )


	except KeyboardInterrupt:
		sys.exit()
		cam0.stop()
		cam1.stop()

	except Exception as e:
		logger.exception("Camera Movement or taking Picture Exception")
		logger.exception(e)

# move the camera back to Origin
def moveCamOrigin(side):
	cordinates = '001001'
	cordinates_encode = cordinates.encode()
	side.write(cordinates_encode)
	time.sleep(1)
	side.flushInput()
	logger.info("Camera came to Origin")



#################################################################################
#																				#
#						Main Block of code Starts here 							#
#																				#
#################################################################################


CTR = 0		# is used inititally to count the iteration of picture samples as of 2019-08-02, this was ignored

SLEEP_TIME = 1800

# Creating datetime Objects
tomorrow =  ( datetime.date.today() + datetime.timedelta(days=1))
tomorrow_start = str(tomorrow) + " "+str(START_TIME)
tomorrow_start_time = datetime.datetime.strptime( str(tomorrow_start),'%Y-%m-%d %H:%M:%S')

today_end = str(datetime.date.today()) + " " +  str(END_TIME)
today_end_time = datetime.datetime.strptime( str(today_end),'%Y-%m-%d %H:%M:%S')

while True:

	now=datetime.datetime.now()
	'''
	if ( now.hour >= today_end_time.hour ):
		# while the script is sleeping, if the pi is restarted then the script wait time will corrupt
		# till the specified start time
		remaining_time = tomorrow_start_time - datetime.datetime.today().replace(microsecond=0)
		x = time.strptime(str(remaining_time),'%H:%M:%S')
		waiting_duration_sec = int( datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds() )
		time.sleep(waiting_duration_sec)
	'''

	for i in range(0, len(CORDINATES_BAY1)):
		cordinate_bay1 = CORDINATES_BAY1[i]
		cordinate_bay2 = CORDINATES_BAY2[i]
		logger.info('bay1 Cam to Move: {}'.format(cordinate_bay1))
		logger.info('bay2 Cam to Move: {}'.format(cordinate_bay2))
		move_cam(cordinate_bay1,BAY1,cam0,"bay1",CTR)
		move_cam(cordinate_bay2,BAY2,cam1,"bay2",CTR)


	moveCamOrigin(BAY1)
	moveCamOrigin(BAY2)

	try:
		s3 = boto3.client('s3', aws_access_key_id=ACCESS_ID,aws_secret_access_key=ACCESS_KEY)
		bucket = 'aigrow-box'
		s3 = boto3.resource('s3', aws_access_key_id=ACCESS_ID,aws_secret_access_key=ACCESS_KEY)
	except Exception as e:
		logger.error("initialise AWS Connection Error")
		logger.error(e)

	else:

		# check if images read properly
		all_data_images = [img for img in glob.glob(IMAGE_FILE_PATH)]

		all_data_log = [img for img in glob.glob(LOG_FILE_PATH)]

		# Log file is set to upload everytime images get uploaded
		if (len(all_data_log)>0):

			curr_time=datetime.datetime.now()

			for in_idx, file_path in enumerate(all_data_log):

				with open(str(file_path),"rb") as log_file:
					name_str=str(file_path).split("_")

					time_str=str(file_path).split("_")[-2]
					time_str = time_str.split("--")
					file_date = datetime.datetime.strptime(time_str[0], '%Y-%m-%d')

					# Create log file everyday
					if ( file_date.date() < curr_time.date() ):
						logger.removeHandler(file_handler)
						logger.removeHandler(stream_handler)

						os.remove(str(file_path))

						file_handler = logging.FileHandler( '/home/pi/Desktop/LogFiles/_{:%Y-%m-%d--%H-%M-%S}_CamTakePic.log'.format(datetime.datetime.now()) )
						file_handler.setFormatter(formatter)
						print("File created")
						stream_handler = logging.StreamHandler()

						logger.addHandler(file_handler)
						logger.addHandler(stream_handler)

						logger.info("Starting the Script-2")

					elif ( file_date.date() == curr_time.date() ):
						# print("can upload the file ")

						try:
							s3.Bucket('aigrow-box').put_object(Key='plant_images/LogFiles/'+name_str[len(name_str)-2]+'_'+name_str[len(name_str)-1],Body=log_file, ContentType='log', ACL='public-read')
						except Exception as e:
							logger.error("Uploading log file error")
							logger.error(e)

		if (len(all_data_images)>0): #If detected images folder, not empty

			for in_idx, img_path in enumerate(all_data_images):  #Loop through all the .jpg files in the folder
				# print(img_path)
				with open(str(img_path),"rb") as image_file:
					name_str=str(img_path).split("_")

					try:
						s3.Bucket('aigrow-box').put_object(Key='plant_images/Images/'+str(name_str[1])+'_'+str(name_str[2])+'_'+str(name_str[3]),Body=image_file, ContentType='image/png', ACL='public-read')
					except Exception as e:
						logger.error("uploading pic error")
						logger.error(e)
					else:
						os.remove(str(img_path))

		# upload aws image url to the API
		all_data_images = [img for img in glob.glob(IMAGE_FILE_PATH)]
		if (len(all_data_images) == 0):

			try:
				# 'token', hashlib.sha1(str(camera_device_ID).encode()).hexdigest().upper()
				data=OrderedDict( [('token', hashlib.sha1( str(camera_device_ID).encode() ).hexdigest().upper() ),('deviceID', str(camera_device_ID) ), ('listOfRecords', [] )] )


				url_data = {'listOfRecords': json.dumps(aws_url_list )}
				data.update(url_data)

				# print(json.dumps(data))

				aws_url_list.clear()

				url ='https://portal.aigrow.lk:12000/InformationController.asmx/addGrowBoxImage'

				headers = {'User-Agent':       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36','Content-Type' : 'application/x-www-form-urlencoded'}

				# data = urllib.parse.urlencode({'token':"F47AEA8BDCBD1179A1F3D91E6AFEEB259488F2D1",'deviceID':"143",'listOfRecords':json.dumps(data2)})
				data = urllib.parse.urlencode(data)
				data = data.encode('utf-8') # data should be bytes
				req = urllib.request.Request(url, data=data,headers=headers)
				resp = urllib.request.urlopen(req)

				respData = json.loads(resp.read().decode('utf-8'))

				# print(resp)
				logger.info(respData)

			except Exception as e:
				logger.error("Uploding to API error")
				logger.error(e)

		logger.info("Finished Uploading")
		# logger.info('Finished Itteration: {}'.format(CTR))

	CTR = CTR + 1

	# After every successful image capture and upload, wait for specified amount of time
	time.sleep(SLEEP_TIME)
