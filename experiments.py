#!/usr/bin/python

from threading import Thread
from time import sleep
import os
import math
import json

from xentop_poller import *

class Experiment(object):

	def __init__(self, nround, client, server, params, XensToVms):
		self.NodeToFile = {}	
		for key, value in XensToVms.iteritems():	
			vms = value
			for vm in vms:
				rate = int(params[2])
				ps = int((rate * math.pow(10,6))/(1000*8))
				name = "%sps_%sm_%s.exp" % (ps, rate, vm)
				expath = "./exp/%s" % name
				self.NodeToFile[vm] = open( expath, "w")
		self.cli = client
		self.ser = server
		self.nround = nround
		self.executor = Thread(target=self.executeExperiment, args=(params,XensToVms))

	def start(self): 
		self.executor.start()
		self.executor.join()

	def executeExperiment(self, params, XensToVms):
		for key, value in XensToVms.iteritems():	
			vms = value
			for vm in vms:
				self.NodeToFile[vm].write("round\t\t\t\t\tavgCPU\t\t\t\t\tvarCPU\t\t\t\t\tdevstdCPU\t\t\t\t\tavgTS\n")
		ip_server = params[0]
		length = int(params[1]) + 5
		rate = params[2]
		for i in range(0, self.nround):
			pollers = []
			print "Client %s vs Server %s: Run %s - Rate %sm" % (self.cli.host, self.ser.host, (i+1), params[2])
			self.cli.start(ip_server, str(length), rate)
			for key, value in XensToVms.iteritems():
				print key, value
				pollers.append(measPoller(int(params[1]), 1, value, key))
			for poller in pollers:
				poller.start()
			for poller in pollers:
				poller.join()
			self.cli.join()
			for key, value in XensToVms.iteritems():	
				vms = value
				for vm in vms:
					self.NodeToFile[vm].write("%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\n" %(i+1, poller.getAvgCPU(vm), poller.getVarCPU(vm), poller.getDEVCPU(vm), poller.getAvgTS(vm)))
			sleep(1)
		for key, value in XensToVms.iteritems():	
			vms = value
			for vm in vms:
				self.NodeToFile[vm].close()

			

	


		
