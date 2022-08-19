import os
import calendar
import time

# Current GMT time in a tuple format
current_GMT = time.gmtime()
# ts stores timestamp
ts = calendar.timegm(current_GMT)

id = "1010"
name = str(id)+'_'+str(ts)
os.system("fswebcam -r 800x600 --no-banner --device /dev/video0  ~/Desktop/code/images/"+name+".jpg",);
