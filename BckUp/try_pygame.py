import os
import pygame, sys

from pygame.locals import *
import pygame.camera

width = 640
height = 480

#initialise pygame   
pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video1",(width,height))
cam.start()

#setup window
# windowSurfaceObj = pygame.display.set_mode((width,height),1,16)
# pygame.display.set_caption('Camera')

#take a picture
# image = cam.get_image()
# cam.stop()

####   display the picture
# catSurfaceObj = image
# windowSurfaceObj.blit(catSurfaceObj,(0,0))
# pygame.display.update()

#save picture
for ind in range(2):
	image = cam.get_image()
	
	pygame.image.save(image,'Images/'+str(ind)+'_picture.jpg')


cam.stop()