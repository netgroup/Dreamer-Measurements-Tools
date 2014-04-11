#!/usr/bin/python
import os
import json
	
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
