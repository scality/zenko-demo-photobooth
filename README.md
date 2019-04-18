# zenko-demo-photobooth
 
## Intro

This is a repository for demo of Zenko multi-cloud replication and metadata search capabilities. 
It is a photobooth that creates animated gifs and writing them as objects to Zenko using s3 API. After the gifs are uplouded to Zenko local storage Orbit allowes to replicate, set lifecicle rules, watch the status of the data on different public clouds.


## Parts

Originally this booth was built and set up using this design [here](https://www.drumminhands.com/2018/06/15/raspberry-pi-photo-booth/). It is very well documented and has a GitHub repo with the base script of photobooth making pictures. You can find all the hardware parts needed and usefull links on how to get started with the pi.
For the demo here I used Raspberry Pi 3, Raspberry Pi camera module and 7 inch HDMI touch display and wired access to the internet because it is infinetally better then wifi that tends to behave very flaky.


## Dependacies 

The operating system of a choice is the latest image of Raspian Stretch Lite (from [here](https://www.raspberrypi.org/downloads/raspbian/)).

Other things:
 ```
   *python 2.7 or later
   *boto3
   *pygame
   *graphicsmagick
```
These can be installed using `sudo apt-get install` or `sudo pip install`


## Demo flow

1. LED light is next to the button and indicates “Ready” status after the pi is booted or previous session is finished. The script runs in an endless loop and launches at boot. This was done by placing [this](https://github.com/scality/zenko-demo-photobooth/blob/master/photobooth.service) script into `/lib/systemd/system/` folder.

2. After the “Start” button was pressed script is executed. User is guided to get ready and Pi Camera Module will take 4 pictures in a row. Resolution can be configured [here](https://github.com/scality/zenko-demo-photobooth/blob/master/config.py).

3. All pictures are saved in `/home/pi` directory. The script calls to `gm` tool and creates an animated gif. Resolution of resulting gif can be also configured.

4. Next step is to provide an input window on the screen for the user to enter their name and email. This two values will be used as metadata for the gif when uploading to Zenko.

5. Upload the gif. Boto is the Amazon Web Services (AWS) SDK for Python. We create a low-level client with the service name ‘s3’ and the keys to Zenko instance along with the endpoint. All this info is available on Orbit connected to Zenko instance.
```
session = boto3.session.Session()

s3_client = session.client(
    service_name='s3',
    aws_access_key_id='ECCESS KEY',
    aws_secret_access_key='SECRET KEY',
    endpoint_url='ZENKO ENDPOINT',)
```
When putting the object to Zenko using client there are few small details to keep in mind.
```
s3_client.put_object(Bucket='transfer-bucket',
    Key= user_name,
    Body=data,
    Metadata={ 'name':user_name, 'email': user_email, 'event': 'dockercon19' })
```
Key- is a string that will be the name to the object(not file path)
Body - is a binary string (that’s why there is a call to open() before)
Metadata - key: value pairs to be added to the object
"transfer-bucket" - is the name of my bucket in Zenko. 
We call it transient source as objects that upoloaded there are deleted right after all desired replications are successfull. This is very handy not to overflow the local Zenko bucket.

6. If everything went well while putting the gif to Zenko then preview mode will start and show the resulting gif to the user couple of times. Instant gratification is important ;)

7. Our freshly created data ready to be managed! At this point, it is a good idea to check the gif in the Orbit browser, make sure that it was replicated to different cloud storage locations, see the metrics, etc.

Thanks to Zenko I have all the gifs of visitors of my photobooth stored and backed up in 3 different cloud storage locations and each object has very handy metadata linked to it. Exactly. Name and email. That allowes me to send all the gifs to their owners without any confusion.

## Credits
Special credit to [@smaffulli](https://github.com/smaffulli/drumminhands_photobooth) as he had the original version of this photobooth running in our office room for fun and generated lots of joy.

[Design](https://www.drumminhands.com/2018/06/15/raspberry-pi-photo-booth/) of the photobooth.



