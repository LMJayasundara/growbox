import boto3
import botocore
import os

import pathlib

access_key = 'AKIAWITJYSJCDXL72IM6'
secret_access_key = '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'
aws_bucket = 'growboximg'

s3client = boto3.client('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_access_key)

name = 'images'

def local_file(folder):
    localFileList = []
    for filename in os.listdir(folder):
        if '.jpg' in filename:
            localFileList.append(filename)
    return localFileList

def s3_file():
    s3FileList = []
    s3 = boto3.resource('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_access_key)
    myBucket = s3.Bucket(aws_bucket)
    for my_bucket_object in myBucket.objects.filter(Prefix=name):
        path = pathlib.PurePath(my_bucket_object.key)
        s3FileList.append(path.name)
    return s3FileList

def upload_file():
    local = local_file(name)
    s3 = s3_file()

    files = [x for x in local if x not in s3]+[x for x in s3 if x not in local]
    return files

files = upload_file()

def upload():

    for file in files:
        upload_file_key = name + '/' + str(file)

        try:
            s3client.upload_file(os.path.join(name, file), aws_bucket, upload_file_key)
            print("Successfully uploaded "+file)

        except FileNotFoundError:
            print("The file was not found")

        except botocore.exceptions.NoCredentialsError:
            print("Credentials not available")

upload()
