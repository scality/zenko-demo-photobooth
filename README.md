# zenko-demo-photobooth
 
## Intro

This is a repository for demo of Zenko multi-cloud replication and metadata search capabilities. 
It is a photobooth that creates animated gifs and writing them as objects to Zenko using s3 API. After the gifs are uplouded to Zenko local storage Orbit allowes to replicate, set lifecicle rules, watch the status of the data on different public clouds.


## Parts

Originally this booth was built and set up using this design [here](https://www.drumminhands.com/2018/06/15/raspberry-pi-photo-booth/). It is very well documented and has a GitHub repo with the base script of photobooth making pictures. You can find all the hardware parts needed and usefull links on how to get started with raspberry pi.
For the demo here I used Paspberry Pi 3, Raspberry Pi camera module and 7 inch HDMI touch display. In my opinion it is using wired access to the internet is infinetally better then wifi because it tends to behave very flaky.


## Dependacies 

The operating system of a choice is the latest image of Raspian Stretch Lite (from [here]https://www.raspberrypi.org/downloads/raspbian/).
Other things:
 ``` 
   *boto3
   *pygame
   *graphicsmagick
```

## Demo flow

LED light is next to the button and indicates “Ready” status after the pi is booted or previous session is finished. The script runs an endless loop and launches at boot. This was done by placing THIS script into THIS folder.
After the “Start” button was pressed script is executed. User is guided to get ready and Pi Camera Module will take 4 pictures in a row. Resolution can be configured HERE.
All pictures are saved in /home/pi directory. The script calls to gm tool and creates an animated gif. Resolution of resulting gif can be also configured.
Next step is to provide an input window on the screen for the user to enter their name and email. This two values will be used as metadata for the gif when uploading to Zenko.
Upload the gif. That is done using boto3. Boto is the Amazon Web Services (AWS) SDK for Python. We create a low-level client with the service name ‘s3’ and the keys to Zenko instance along with the endpoint. All this info is available on Orbit connected to Zenko instance.
[snippet]
When putting the object to Zenko using client there are few small details to keep in mind:
Key - is a string that will be the name to the object(not file path)
Body - is a binary string (that’s why there is a call to open() before)
Metadata - key: value pairs to be added to the object

6. I everything went well putting the gif to Zenko then preview mode will start and show the resulting gif to the user couple times. Instant gratification is important ;)
 7. Our freshly created data ready to be managed! At this point, it is a good idea to check the gif in the Orbit browser, make sure that it was replicated to different cloud storage locations, see the metrics…

## Credits
Special credit to [@smaffulli](https://github.com/smaffulli/drumminhands_photobooth) as he had the original version of this photobooth running in our office room before for fun and generated lots of joy.
[Design](https://www.drumminhands.com/2018/06/15/raspberry-pi-photo-booth/)



