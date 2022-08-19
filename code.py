#!/usr/bin/env python3
import serial
import time
import os
import calendar

CORDINATES_BAY1 = ["0125","5025","5050","9950","9901"]

def moveCamOrigin(ser):
    cordinate = "9999"
    cordinates_encode = cordinate.encode()
    ser.write(cordinates_encode)
    ser.flushInput()
    time.sleep(3)

def moveCam(cod, ser):
    cordinates_encode = cod.encode()
    ser.write(cordinates_encode)
    ser.flushInput()
    # captureImg(cod)
    time.sleep(3)

def captureImg(cod):
    current_GMT = time.gmtime()
    ts = calendar.timegm(current_GMT)
    name = str(cod)+'_'+str(ts)
    os.system("fswebcam -r 800x600 --no-banner --device /dev/video0  ~/Desktop/code/images/"+name+".jpg");
    time.sleep(2)

def run(ser):
    while True:
        try:
            position = str(ser.readline().decode('utf-8').rstrip())
            if(position != ""):
                print(position)
                captureImg(position)

                if(position == "Home"):
                    ser.flushInput()
                    moveCam(CORDINATES_BAY1[0], ser)

                # if(position == CORDINATES_BAY1[0]):
                #     ser.flushInput()
                #     moveCam(CORDINATES_BAY1[1], ser)
                # if(position == CORDINATES_BAY1[1]):
                #     ser.flushInput()
                #     moveCam(CORDINATES_BAY1[2], ser)

                if(position != "Home" and position != CORDINATES_BAY1[len(CORDINATES_BAY1)-1]):
                    for index, item in enumerate(CORDINATES_BAY1[:-1]):
                        if(position == CORDINATES_BAY1[index]):
                            ser.flushInput()
                            moveCam(CORDINATES_BAY1[index+1], ser)

                if(position == CORDINATES_BAY1[len(CORDINATES_BAY1)-1]):
                    ser.flushInput()
                    moveCamOrigin(ser)
                else:
                    pass
            else:
                pass
        except (KeyboardInterrupt, SystemExit):
            moveCamOrigin(ser)
            raise

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    ser.reset_input_buffer()
    moveCamOrigin(ser)
    run(ser)
