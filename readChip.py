#Written for Python3
#This module is the standard function for scanning RFID-Chips.
#Used throughout the whole project, the programmer can give a time in
#Seconds that the Programm should wait for a chip to be put on the scanner.
#After that, the scanning procedure is aborted.
import RPi.GPIO as GPIO
import MFRC522
import sys
import os
import time
mfrc = MFRC522.MFRC522()
def scan():
		global mfrc
		uid = False
	 # Scan for cards    
		(status,TagType) = mfrc.MFRC522_Request(mfrc.PICC_REQIDL)
		# If a card is found
		if status == mfrc.MI_OK:
			print ("Card detected")
		# Get the UID of the card
			(status,uid) = mfrc.MFRC522_Anticoll()
		if not uid:
			return "0"
		else:
			tmp=""
			for id in uid:
				tmp = tmp + str(id)
			return tmp
