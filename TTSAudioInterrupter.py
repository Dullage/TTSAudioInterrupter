#!/usr/bin/env python
import paho.mqtt.client as mqtt
from gtts import gTTS
import os
import time


# USER PARAMETERS #
# Set the volume levels that work best for you
normalInputVolume = 50
reducedInputVolume = 0
normalOutputVolume = 50

# Location of the "notification" WAV file that is played before the text
notificationSoundFile = "/home/pi/TTSAudioInterrupter/notification.wav"

# A directory in which to download (cache) the TTS MP3
workingDirectory = "/home/pi/TTSAudioInterrupter"

# MQTT Credentials
MQTTIPAddress = "REDACTED"
MQTTPort = 1883
MQTTUserName = "REDACTED"
MQTTPassword = "REDACTED"
MQTTTopic = "tts"
# END OF USER PARAMETERS #


# Function to set the input volume level using Alsa Mixer
def setInputVolume(volume):
	os.system("amixer set Mic {0}%".format(volume)) # Mic refers to the name of my input, you may need to change this

# Function to set the output volume level using Alsa Mixer
def setOutputVolume(volume):
	os.system("amixer set Speaker {0}%".format(volume)) # Speaker refers to the name of my output, you may need to change this

# Setup the MQTT Connection
connected = False
while connected == False:
	try:
		client = mqtt.Client()
		client.username_pw_set(MQTTUserName, password=MQTTPassword)
		client.connect(MQTTIPAddress, MQTTPort, 60)
		connected = True
	except:
		print("Connection Failed! Retrying in 3s...")
		time.sleep(3)

# When connected, subscribe to the appropriate topic
def on_connect(client, userdata, flags, rc):
	client.subscribe(MQTTTopic)

# This is what happens when an MQTT message is sent to the subscribed topic
def on_message(client, userdata, msg):
	topic = msg.topic.decode('utf-8')

	if topic == MQTTTopic: # We are only subscribed to 1 topic but this could be useful if others are added
		message = msg.payload.decode('utf-8')
		print(message) # Useful for debugging
		
		tts = gTTS(text=message, lang='en') # Ask Google for the TTS MP3 file
		tts.save("{0}/tts.mp3".format(workingDirectory)) # Save it to the working directory
		
		setInputVolume(reducedInputVolume) # Lower the input volume
		time.sleep(0.5) # Wait half a second (sounds better)
		os.system("aplay {0}".format(notificationSoundFile)) # Use Alsa Play to play the notification WAV file
		os.system("mpg123 {0}/tts.mp3".format(workingDirectory)) # Use mpg123 to play the TTS MP3 file
		setInputVolume(normalInputVolume) # Return the input volume to normal

# These 2 lines ensure the volumes are set to normal upon startup
setInputVolume(normalInputVolume)
setOutputVolume(normalOutputVolume)

# Connect to the MQTT server, bind the on_message function and then loop forever
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()