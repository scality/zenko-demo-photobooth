#!/usr/bin/env python
# created by chris@drumminhands.com
# see instructions at http://www.drumminhands.com/2014/06/15/raspberry-pi-photo-booth/

import os
import glob
import time
import traceback
from time import sleep
import RPi.GPIO as GPIO
import picamera # http://picamera.readthedocs.org/en/release-1.4/install2.html
import atexit
import sys
import socket
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
import config
from signal import alarm, signal, SIGALRM, SIGKILL
import requests
import json
import base64
import pygame_textinput
import boto3

########################
### Variables Config ###
########################
led_pin = 7 # LED
btn_pin = 18 # pin for the start button

total_pics = 4 # number of pics to be taken
capture_delay = 1 # delay between pics
prep_delay = 5 # number of seconds at step 1 as users prep to have photo taken
gif_delay = 30 # How much time between frames in the animated gif
restart_delay = 20 # how long to display finished message before beginning a new session
test_server = 'www.google.com'

high_res_w = 1920 # width of high res image, if taken
high_res_h = 1152 # height of high res image, if taken


#############################
### Variables that Change ###
#############################
# Do not change these variables, as the code will change it anyway
transform_x = config.monitor_w # how wide to scale the jpg when replaying
transfrom_y = config.monitor_h # how high to scale the jpg when replaying
offset_x = 0 # how far off to left corner to display photos
offset_y = 0 # how far off to left corner to display photos
replay_delay = 1 # how much to wait in-between showing pics on-screen after taking
replay_cycles = 2 # how many times to show each photo on-screen after taking

####################
### Other Config ###
####################
real_path = os.path.dirname(os.path.realpath(__file__))
emails_path = '/home/pi/drumminhands_photobooth/emails'

# GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin,GPIO.OUT) # LED
GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(led_pin,False) #for some reason the pin turns on at the beginning of the program. Why?

# initialize pygame
pygame.init()
pygame.display.set_mode((config.monitor_w, config.monitor_h))
screen = pygame.display.get_surface()
pygame.display.set_caption('Photo Booth Pics')
pygame.mouse.set_visible(False) #hide the mouse cursor

#pygame.display.toggle_fullscreen()

#################
### Functions ###
#################

# function to receive text input from customer
# using pygme-text-input module
def capture_text(flag):
    textinput = pygame_textinput.TextInput()

    screen = pygame.display.set_mode((800, 480))
    clock = pygame.time.Clock()
    while True:
        screen.fill((255, 204, 128))
        events = pygame.event.get()
        for event in events:
		if event.type == pygame.QUIT:
                	exit()

        screen.blit(textinput.get_surface(), (20, 20))
        pygame.display.update()
        clock.tick(100)
        if textinput.update(events):
		capture = textinput.get_text()
		tofile=capture + '\n'
		if flag==1:
			tofile = capture + '\n\n'
            	wr_file = open(emails_path, mode='a')
            	wr_file.write(tofile)
            	wr_file.close()
            	print(capture)
            	pygame.display.update()
            	break
    return(capture)

# clean up running programs as needed when main program exits
def cleanup():
  print('Ended abruptly')
  pygame.quit()
  GPIO.cleanup()
atexit.register(cleanup)

# A function to handle keyboard/mouse/device input events
def input(events):
    for event in events:  # Hit the ESC key to quit the slideshow.
        if (event.type == QUIT or
            (event.type == KEYDOWN and event.key == K_ESCAPE)):
		pygame.quit()
		sys.exit(0)

#delete files in folder
def clear_pics(channel):
	files = glob.glob(config.file_path + '*')
	for f in files:
		os.remove(f)
	#light the lights in series to show completed
	print "Deleted previous pics"
	for x in range(0, 3): #blink light
		GPIO.output(led_pin,True);
		sleep(0.25)
		GPIO.output(led_pin,False);
		sleep(0.25)

# check if connected to the internet
def is_connected():
  try:
    # see if we can resolve the host name -- tells us if there is a DNS listening
    host = socket.gethostbyname(test_server)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False

# set variables to properly display the image on screen at right ratio
def set_demensions(img_w, img_h):
	# Note this only works when in booting in desktop mode.
	# When running in terminal, the size is not correct (it displays small). Why?

    # connect to global vars
    global transform_y, transform_x, offset_y, offset_x

    # based on output screen resolution, calculate how to display
    ratio_h = (config.monitor_w * img_h) / img_w

    if (ratio_h < config.monitor_h):
        #Use horizontal black bars
        #print "horizontal black bars"
        transform_y = ratio_h
        transform_x = config.monitor_w
        offset_y = (config.monitor_h - ratio_h) / 2
        offset_x = 0
    elif (ratio_h > config.monitor_h):
        #Use vertical black bars
        #print "vertical black bars"
        transform_x = (config.monitor_h * img_w) / img_h
        transform_y = config.monitor_h
        offset_x = (config.monitor_w - transform_x) / 2
        offset_y = 0
    else:
        #No need for black bars as photo ratio equals screen ratio
        #print "no black bars"
        transform_x = config.monitor_w
        transform_y = config.monitor_h
        offset_y = offset_x = 0

    # uncomment these lines to troubleshoot screen ratios
        print str(img_w) + " x " + str(img_h)
        print "ratio_h: "+ str(ratio_h)
        print "transform_x: "+ str(transform_x)
        print "transform_y: "+ str(transform_y)
        print "offset_y: "+ str(offset_y)
        print "offset_x: "+ str(offset_x)

# display one image on screen
def show_image(image_path):

	# clear the screen
	screen.fill( (0,0,0) )

	# load the image
	img = pygame.image.load(image_path)
	img = img.convert()

	# set pixel dimensions based on image
	set_demensions(img.get_width(), img.get_height())

	# rescale the image to fit the current display
	img = pygame.transform.scale(img, (transform_x,transfrom_y))
	screen.blit(img,(offset_x,offset_y))
	pygame.display.flip()

# display a blank screen
def clear_screen():
	screen.fill( (0,0,0) )
	pygame.display.flip()

# display a group of images
def display_pics(jpg_group):
    for i in range(0, replay_cycles): #show pics a few times
		for i in range(1, total_pics+1): #show each pic
			show_image(config.file_path + jpg_group + "-0" + str(i) + ".jpg")
			time.sleep(replay_delay) # pause


# On screen text message
def displayStatus(status, size):
        screen.fill((255, 204, 128))

        font = pygame.font.SysFont("roboto",size, bold=True)
        text = font.render(status,True,(0,51,0))

        # Display in the center of the screen
        textrect = text.get_rect()
        textrect.centerx = screen.get_rect().centerx
        textrect.centery = screen.get_rect().centery

        screen.blit(text,textrect)

        pygame.display.flip() # update the display


def make_gif(now):
	#get the current date and time for the start of the filename
	if config.hi_res_pics:
		# first make a small version of each image. Tumblr's max animated gif's are 500 pixels wide.
		for x in range(1, total_pics+1): #batch process all the images
			graphicsmagick = "gm convert -size 500x500 " + config.file_path + now + "-0" + str(x) + ".jpg -thumbnail 500x500 " + config.file_path + now + "-0" + str(x) + "-sm.jpg"
			os.system(graphicsmagick) #do the graphicsmagick action

		graphicsmagick = "gm convert -delay " + str(gif_delay) + " " + config.file_path + now + "*-sm.jpg " + config.file_path + now + ".gif"
		os.system(graphicsmagick) #make the .gif
	else:
		# make an animated gif with the low resolution images
		graphicsmagick = "gm convert -delay " + str(gif_delay) + " " + config.file_path + now + "*.jpg " + config.file_path + now + ".gif"
		os.system(graphicsmagick) #make the .gif


# the photo taking function for when the big button is pressed
def start_photobooth():

	input(pygame.event.get()) # press escape to exit pygame. Then press ctrl-c to exit python.

	################################# Begin Step 1 #################################

	print "Get Ready"
	GPIO.output(led_pin,False);
	show_image(real_path + "/guidelines/instructions.png")
	sleep(prep_delay)

	# clear the screen
	clear_screen()

	camera = picamera.PiCamera()
	camera.vflip = True # since the camera is upside down
	camera.hflip = True # flip for preview, showing users a mirror image
	#camera.saturation = -100 # comment out this line if you want color images
	camera.iso = config.camera_iso
	camera.rotation = 270

	pixel_width = 0 # local variable declaration
	pixel_height = 0 # local variable declaration

	if config.hi_res_pics:
		camera.resolution = (high_res_w, high_res_h) # set camera resolution to high res
	else:
		pixel_width = 500 # maximum width of animated gif on tumblr
		pixel_height = config.monitor_h * pixel_width // config.monitor_w
		camera.resolution = (pixel_width, pixel_height) # set camera resolution to low res

	################################# Begin Step 2 #################################

	print "Taking pics"

	now = time.strftime("%Y-%m-%d-%H-%M-%S") #get the current date and time for the start of the filename

	if config.capture_count_pics:
		try: # take the photos
			for i in range(1,total_pics+1):

				displayStatus(str(i), 200)
				camera.hflip = True # preview a mirror image
				#camera.start_preview(resolution=(config.monitor_w, config.monitor_h)) # start preview at low res but the right ratio
				camera.start_preview() # let the camera start as it wants to
				time.sleep(2) #warm up camera
				GPIO.output(led_pin,True) #turn on the LED
				filename = config.file_path + now + '-0' + str(i) + '.jpg'
				#camera.hflip = True # was False # flip back when taking photo
				camera.capture(filename)
				print(filename)
				GPIO.output(led_pin,False) #turn off the LED

				#camera.stop_preview()
				#show_image(real_path + "/pose" + str(i) + ".png")
				# use pygame superimpose to show countdown to next pose
				time.sleep(capture_delay) # pause in-between shots
				clear_screen()
				if i == total_pics+1:
					break
		finally:
			camera.close()
	else:
		camera.start_preview(resolution=(config.monitor_w, config.monitor_h)) # start preview at low res but the right ratio
		time.sleep(2) #warm up camera

		try: #take the photos
			for i, filename in enumerate(camera.capture_continuous(config.file_path + now + '-' + '{counter:02d}.jpg')):
				GPIO.output(led_pin,True) #turn on the LED
				print(filename)
				time.sleep(capture_delay) # pause in-between shots
				GPIO.output(led_pin,False) #turn off the LED
				if i == total_pics-1:
					break
		finally:
			camera.stop_preview()
			camera.close()

	########################### Begin Step 3 #################################

	input(pygame.event.get())

        displayStatus("Please enter your first and last name",42)
        sleep(prep_delay)

        user_name = capture_text(0) #store user name first and last

        displayStatus("Please enter your email address",42)
        sleep(prep_delay)
        user_email = capture_text(1) #store user email


	show_image(real_path + "/guidelines/processing.png")


	if config.make_gifs: # make the gifs
		print "Creating an animated gif"
		make_gif(now)
	if config.post_online:
            connected = is_connected()
            ################### SET UP ZENKO ENDPOINT ##################

            if (connected==False):
		print "Oops. No internect connection. Upload later."
                #make a text file as a note to upload the .gif later
		displayStatus("Oops. There is no internet connection.\nUpload later.", 42)
                try:
			file = open(config.file_path + now + "-FILENOTUPLOADED.txt",'w')   # Trying to create a new file or open one
                    	file.close()
                except:
			print('Something went wrong. Could not write file.')
		    	sys.exit(0) # quit Python
            while connected:
		session = boto3.session.Session()

                s3_client = session.client(
                    service_name='s3',
                    aws_access_key_id='3WS0VKFA6WD08Y8QZBUN',
                    aws_secret_access_key='oZ/XljCBdRTDhhyZc=9WzO8cd7ecEbaQ0JFmniiq',
                    endpoint_url='https://53dc7c09-57d5-11e9-bde1-c606aa6eabf1.sandbox.zenko.io',)
		if config.make_gifs:
                    try:
			file_to_upload = config.file_path + now + ".gif"
			data= open(file_to_upload,'rb')
			print ("Opened in binary")
			s3_client.put_object(Bucket='zenkolocal',
				Key= user_name,
                        	Body=data,
                        	Metadata={ 'name':user_name, 'email': user_email, 'event': 'dockercon19' })
                        break
                    except:
			print('Something went wrong with uplouding to Zenko.')
                        sys.exit(0) # quit Python




	########################### Begin Step 4 #################################

	input(pygame.event.get()) # press escape to exit pygame. Then press ctrl-c to exit python.

	try:
		display_pics(now)
	except Exception, e:
		tb = sys.exc_info()[2]
		traceback.print_exception(e.__class__, e, tb)
		pygame.quit()

	print "Done"
	displayStatus("Your animated gif was uplouded to Zenko! :D",42)
	time.sleep(prep_delay)
	show_image(real_path + "/guidelines/finished2.png")

	time.sleep(restart_delay)
	show_image(real_path + "/guidelines/intro.png")
	GPIO.output(led_pin,True)

####################
### Main Program ###
####################

## clear the previously stored pics based on config settings
if config.clear_on_startup:
	clear_pics(1)

print "Photo booth app running..."
for x in range(0, 5): #blink light to show the app is running
	GPIO.output(led_pin,True)
	sleep(0.25)
	GPIO.output(led_pin,False)
	sleep(0.25)

show_image(real_path + "/guidelines/intro.png");

while True:
	GPIO.output(led_pin,True); #turn on the light showing users they can push the button
	input(pygame.event.get()) # press escape to exit pygame. Then press ctrl-c to exit python.
	GPIO.wait_for_edge(btn_pin, GPIO.FALLING)
	time.sleep(config.debounce) #debounce
	start_photobooth()
