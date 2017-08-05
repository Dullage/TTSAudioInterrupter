#!/usr/bin/env python	
import paho.mqtt.client as mqtt
from gtts import gTTS
import time
import os
import vlc

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
MQTTTTSTopic = "tts" # Any text received on this topic will be read out by gTTS
MQTTAudioFileTopic = "audio" # Send a file name on this topic and as long as it's in the working directory it will be played
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
	client.subscribe(MQTTTTSTopic)
	client.subscribe(MQTTAudioFileTopic)

# This is what happens when an MQTT message is sent to the subscribed topic
def on_message(client, userdata, msg):
	topic = msg.topic.decode('utf-8')

	# TTS Reader
	if topic == MQTTTTSTopic:
		message = msg.payload.decode('utf-8')
		print(message) # Useful for debugging
		
		tts = gTTS(text=message, lang='en-uk') # Ask Google for the TTS MP3 file
		tts.save("{0}/tts.mp3".format(workingDirectory)) # Save it to the working directory
		
		setInputVolume(reducedInputVolume)
		
		time.sleep(0.5) # Wait half a second, sounds better
		
		# Play the notification sound
		player.set_media(notificationFile)
		player.play()
		while (player.get_state() != 6): # While the file has not finished playing
			pass # Wait
		
		# Play the TTS audio file
		player.set_media(ttsFile)
		player.play()
		while (player.get_state() != 6): # While the file has not finished playing
			pass # Wait
		
		setInputVolume(normalInputVolume) # Return the input volume to normal
		
	# Custom Audio File Player
	elif topic == MQTTAudioFileTopic:
		message = msg.payload.decode('utf-8')
		print(message) # Useful for debugging
		
		audioFile =  instance.media_new("{0}/{1}".format(workingDirectory, message))
		
		setInputVolume(reducedInputVolume)
		
		time.sleep(0.5) # Wait half a second, sounds better
		
		# Play the specified audio file
		player.set_media(audioFile)
		player.play()
		while (player.get_state() != 6): # While the file has not finished playing
			pass # Wait
		
		setInputVolume(normalInputVolume) # Return the input volume to normal

instance = vlc.Instance() # Start an instance of VLC
player = instance.media_player_new() # Create a new VLC player 
notificationFile = instance.media_new(notificationSoundFile) # Tell VLC about the notification sound file
ttsFile = instance.media_new(workingDirectory + '/tts.mp3') # Tell VLC about the tts sound file
		
# These 2 lines ensure the volumes are set to normal upon start-up
setInputVolume(normalInputVolume)
setOutputVolume(normalOutputVolume)

# Connect to the MQTT server, bind the on_message function and then loop forever
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()
