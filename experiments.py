#!/usr/bin/python

from threading import Thread
from time import sleep
import os
import math
import json

from xentop_poller import *
from experiments_utils import isNumber

class Experiment(object):

	def __init__(self, nround, client, server, params, XensToVms):
		self.NodeToFile = {}	
		for key, value in XensToVms.iteritems():	
			vms = value
			for vm in vms:
				rate = params[2]
				ps = (rate * math.pow(10,6))/(1000*8)
				name = "%sps_%sm_%s.exp" % (ps, rate, vm)
				path = "exp/"
				if os.path.exists(path) == False:
					os.mkdir(path, 0755)
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
				self.NodeToFile[vm].write("round(N)\t\t\tavgCPU(%)\t\t\tvarCPU(%)\t\t\tdevstdCPU(%)\t\t\tavgTS(%)\t\t\tjitter(ms)\t\t\tloss(%)\n")
		ip_server = params[0]
		rate = params[2]
		interval = params[3]
		length = (params[1])*(interval*2)
		delay = params[4]
		
		consec_error = 0
		exper_error = 0
		limit_consec = int(self.nround/4)
		limit_exper = int(self.nround/2)
	
		print "Max Sporadic Errors %s - Consecutive Errors %s" %(limit_exper, limit_consec)
		i = 0
		while i < self.nround:
			if (consec_error == limit_consec or exper_error == limit_exper):
				print "Exit...Reach Limit"
				break	
			XensToPollers = {}
			print "Client %s vs Server %s: Run %s - Rate %sm" % (self.cli.host, self.ser.host, (i+1), params[2])
			self.cli.start(ip_server, str(length), rate)
			for xen, vms in XensToVms.iteritems():
				XensToPollers[key]=(measPoller(params[1], interval, vms, xen, delay))
			for xen, poller in XensToPollers.iteritems():
				poller.start()
			for xen, poller in XensToPollers.iteritems():
				poller.join()
			self.cli.join()
			jitter = "N/A"
			loss = "N/A"
			jitter = self.cli.getJitter()
			loss = self.cli.getLoss()
			for key, value in XensToVms.iteritems():	
				vms = value
				for vm in vms:
					self.NodeToFile[vm].write("%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\t\t\t\t%s\n" %(i+1, XensToPollers[key].getAvgCPU(vm),  XensToPollers[key].getVarCPU(vm),  XensToPollers[key].getDEVCPU(vm),  XensToPollers[key].getAvgTS(vm), jitter, loss))
			if (isNumber(loss) and float(loss) < 1.0):
				consec_error = 0
				i = i + 1
			else:
				print "Error Too Loss %s Repeat Run - After %s Consecutive Error Or %s Sporadic Error The Experiment Stops" %(loss, limit_consec, limit_exper)
				consec_error = consec_error + 1
				exper_error = exper_error + 1	
			sleep(2)
		for key, value in XensToVms.iteritems():	
			vms = value
			for vm in vms:
				self.NodeToFile[vm].close()

			

	


		
