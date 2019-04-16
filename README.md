# zenko-demo-photobooth
 
## Intro
This is a repository for demo of Zenko multi-cloud replication and metadata search capabilities. 
It is a photobooth that creates animated gifs and writing them as objects to Zenko using s3 API. After the gifs are uplouded to Zenko local storage Orbit allowes to replicate, set lifecicle rules, watch the status of the data on different public clouds.

## Demo flow

1. Booth displays the instruction picture to press the "Start" button
2. After the button was pressed python script starts (pygame). It will automatically take 4 pictures.
3. Script creates animated gif from images and displays it in preview mode on the booth's screen.
4. Object will be created from the gif with name and email of a user as metadata. This will be uploaded to Zenko local bucket using s3 API.
5. Once the object is uploaded Orbit will start replication to 3 cloud storage locations (GCP, AWS, Azure) automatically.
After successful replication object will be deleted from local Zenko file system to preserve space.

## Parts
Originally this booth was built and set up using this design. It is very well documented and has a GitHub repo with the base script of photobooth making pictures. You can find all the hardware parts needed and usefull links on how to get started with raspberry pi.
For the demo here I used Paspberry Pi 3, Raspberry Pi camera module and 7 inch HDMI touch display. Special credit to @smaffulli as he had the original version of this photobooth running in our office room before to fun moments for the team.

## Dependacies 
The operating system of a choice is the latest image of Raspian Stretch Lite (find them here https://www.raspberrypi.org/downloads/raspbian/). 
