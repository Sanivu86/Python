#@Authors Anastassia Pellja, Sanna Nieminen-Vuorio
from gpiozero import LED
import keyboard
import threading
from gpiozero import DistanceSensor
from time import sleep
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from picamera import PiCamera
import http.client
import urllib

#All the variables

#Leds specified
green = LED(21)
red = LED(20)
yellow = LED(16)
#Distance sensor for monitoring if someone is on the door
sensor = DistanceSensor(19, 6)
#Brokeraddress and client for Mqtt
broker_address = "192.168.0.17"
client = mqtt.Client()

#Thread for detecting someone on the door and taking a picture on him/her
class threadPhoto(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("Starting " + self.name)
        sendPhoto(self.name)
        print("Existing " + self.name)

#Thread for monitoring if user opens or closes the door
class threadLight(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("Starting " + self.name)
        turnOnLight(self.name)
        print("Existing " + self.name)

#Function to detect if user open or closes the door.
#Simulated, so user presses 'o' on the keyboard to open the door and 'c' to close.
#Lights go on depending the press and if door is opened, the time will be send to thingspeak
def turnOnLight(threadName):
    while True:
        if(keyboard.is_pressed('o')):
            print("You may come in") 
            red.off()
            green.on()
            sleep(3)
            green.off()
            sendToThing() #time sent to ThingSpeak
            
        if(keyboard.is_pressed('c')):
            print("Don't come in")
            red.on()
            green.off()
            sleep(3)
            green.off()
            
        else:
            red.off()
            green.off()
            
#Enable camera outside of the loop, so it's enabled just once
camera = PiCamera()

#Funtion to take a picture. Saved to photos-folder
def takePicture():
    camera.resolution = (1024, 768)
    camera.start_preview()
    camera.capture('./photos/foo.jpg')
    camera.stop_preview()
    

#Function to detect if someone is on the door.
#If distancesensor detects someone less than 1m away and the time is not the same than last time,
#function takes a photo and send it to subscriber. Yellow light goes on.
def sendPhoto(threadName):
    time1=1
    while True:
        if sensor.distance < 1.0:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            if time1 != current_time: #Checking the time, so it don't take pictures all the time
                yellow.on()
                sleep(1)
                print("Someone on the door")
                takePicture()
                f = open("./photos/foo.jpg", "rb") 
                fileContent = f.read()
                image = bytearray(fileContent)
                sleep(1)
                time1=current_time

                client.connect(broker_address, 1883, 60)

                client.loop_start()  
                client.publish("/etsidi/val", image) 
                client.disconnect()
                client.loop_stop()

        else:
            yellow.off()
        sleep(1)

#Function to connect MQTT
def on_connect(client, userdata, flags, rc):
    m="Connected flags: " + str(flags) + " result code: " + str(rc) + " client1_id: " + str(client)
    print(m)
    
#Function to send a time to thingspeak. Used when user opens the door
def sendToThing():
    
    key = "GWKKBTMB0Y4T3F7L" #API key

    now = datetime.now()
    current_time = now.strftime("%H:%M")
    params = urllib.parse.urlencode({'field1': current_time, 'key':key })
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    conn = http.client.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()

    print(response.status, response.reason)
    data = response.read()
    print (data)
    print ("Time sent to thinkSpeak")

    conn.close()
        
# Create the Threads
thread1 = threadPhoto(1, "Photo-Thread")
thread2 = threadLight(2, "Light-Thread")

# Start the Threads
thread1.start()
thread2.start()

# Wait for finishing the Threads
thread1.join()
print("Main Thread dies")
thread2.join()