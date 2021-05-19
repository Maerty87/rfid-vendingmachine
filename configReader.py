#Written for Python3
#This code reads multiple config-Files from the "conf"-Direectory and returns a dictionary with key-value pairs
#for simple import
# The format for the .conf file is:
# KEYNAME = VALUE
# Every line starting with # gets ignored
# whitespaces will be ignored.
# currently only the following entries are supported

import os
import sys
path = "./config/"
files = os.listdir(path)
tmpList = {} 
def parseFile(filter):
	global tmpList
	for file in files:
		with open(path+file,"r") as inputfile:
			for line in inputfile:
				if line.startswith("#"):
					continue
				elif line.strip()== "":
					continue
				else:
					splt = line.strip()
					splt = splt.split('=')
					splt[0] = splt[0].strip()
					splt[1] = splt[1].strip() 
					tmpList[splt[0]]=splt[1]
	if filter == None:
		return tmpList
	elif filter == "db":
		tmp = {}
		for entry in tmpList:
			if entry.startswith("db"):
				tmp[entry] = tmpList[entry]
		return tmp
	elif filter == "app":
		tmp = {}
		for entry in tmpList:
			if entry.startswith("app"):
				tmp[entry] = tmpList[entry]
		return tmp
	elif filter == "ch":
		tmp = {}
		for entry in tmpList:
			if entry.startswith("ch"):
				tmp[entry] = tmpList[entry]
		return tmp

