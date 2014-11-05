#!/usr/bin/python
import os
import json
import shutil
import unicodedata
import sys
	
def load_conf():
	if os.path.exists(".conf") == False:
		print "Error Create Configuration File .conf"
		sys.exit(-2)
	conf = open(".conf")
	json_data = json.load(conf)
	username = json_data['username']
	password = json_data['password']
	conf.close()
	return (username, password)

def clean_environment():
	folder = './log'
	if os.path.exists(folder):
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				    os.unlink(file_path)
			except Exception, e:
				print e

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
	return False
