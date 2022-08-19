import os
import pygame, sys

from pygame.locals import *
import pygame.camera

width = 1280
height = 960

#initialise pygame   
pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0",(width,height))
cam.start()

#setup window
# windowSurfaceObj = pygame.display.set_mode((width,height),1,16)
# pygame.display.set_caption('Camera')

#take a picture
ctr = 0
while ctr < 8:
	image = cam.get_image()
	ctr = ctr + 1

####   display the picture
# catSurfaceObj = image
# windowSurfaceObj.blit(catSurfaceObj,(0,0))
# pygame.display.update()

#save picture
pygame.image.save(image,'picture.jpg')


cam.stop()
