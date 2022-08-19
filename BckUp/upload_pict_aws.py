import os
import time
import json
import ast
import hashlib
import urllib.request
import urllib.parse
import boto3
import datetime
import glob
import hashlib

from collections import OrderedDict


#Access IDs for AWS upload
ACCESS_ID = 'AKIAIRPU2BADUGM4MAXQ'
ACCESS_KEY = '40lFoFFB2rtBVqoygomIwrXVzNzl3AxhpQD0k7t4'


# make this as a function (upload to AWS)

s3 = boto3.client('s3', aws_access_key_id=ACCESS_ID,aws_secret_access_key=ACCESS_KEY)
bucket = 'aigrow-box'
s3 = boto3.resource('s3', aws_access_key_id=ACCESS_ID,aws_secret_access_key=ACCESS_KEY)

# check if images read properly
all_data_1 = [img for img in glob.glob("/home/pi/Desktop/Images/*jpg")]
# all_data_1 = [img for img in glob.glob("/home/antony/Documents/AIGrow/AiGrowBox/Images/*jpg")]

# print(len(all_data_1))

if (len(all_data_1)>0): #If detected images folder, not empty
	
	for in_idx, img_path in enumerate(all_data_1):  #Loop through all the .jpg files in the folder
		# print(img_path)
		with open(str(img_path),"rb") as imageFile:
			name_str=str(img_path).split("_")

			s3.Bucket('aigrow-box').put_object(Key='plant_images/WEEK2/plant_'+str(name_str[1])+str(name_str[2])+str(name_str[3]),Body=imageFile, ContentType='image/png', ACL='public-read')
			
			os.remove(str(img_path))
			print("finish one")
