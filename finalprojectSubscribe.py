#@Authors Anastassia Pellja, Sanna Nieminen-Vuorio
import paho.mqtt.client as mqtt
from time import sleep
import http.client
import urllib
import time
from datetime import datetime

#Allvariables
broker_address = "192.168.0.17"
client = mqtt.Client() 

#Connect to MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("/etsidi/#")

#Get a image from MQTT and save it to photos-folder with timestamp
def on_message(client1, userdata, message):
    now = datetime.now()
    current_time = now.strftime('%m-%d %a %H:%M')
    f = open('./photos/doorPicture'+current_time+'.jpg', "wb")
    f.write(message.payload)
    print("Image Received")
    f.close()
  
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.17", 1883, 60)
client.loop_forever()
