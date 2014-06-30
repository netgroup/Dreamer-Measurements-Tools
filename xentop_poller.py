#!/usr/bin/python

import socket
import json
import time
import math
from threading import Thread
from collections import defaultdict
import re
import string

class measPoller(object):
	
	XENPORT = 8888
	MSIZE = 1024
	KEYCPU = 'cpu_perc'
	KEYTS = 'timestamp'

	def __init__(self, length, interval, vms, xenaddr, delay):
		self.cpu_perc = defaultdict(list)
		self.ts = defaultdict(list)
		self.thread = Thread(target = self.getVMTop, args=(length, interval, vms, xenaddr, delay))
		self.NodeToavgCPU = {}
		self.NodeTovarCPU = {}
		self.NodeToavgTS = {}
		self.NodeTovarTS = {}
		for vm in vms:
			self.NodeToavgCPU[vm] = 0.0
			self.NodeTovarCPU[vm] = 0.0
			self.NodeToavgTS[vm] = 0.0
			self.NodeTovarTS[vm] = 0.0

	def	start(self):
		self.thread.start()
	
	def join(self):
		self.thread.join()

	def getVMTop(self, length, interval, vm, xenaddr, delay):
		request = {'message':'getVMTop', 'vm_list':vm}
		for i in range(0, length):
			ts_start = time.time()
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((xenaddr, self.XENPORT))
			s.send(json.dumps(request))
			result = json.loads(s.recv(self.MSIZE))
			if delay > 0:
				delay = delay - 1
			else :
				for vminfo in result:
					self.cpu_perc[vminfo['name']].append(float(vminfo[self.KEYCPU]))
					self.ts[vminfo['name']].append(float(vminfo[self.KEYTS]))
			s.close()
			ts_end = time.time()
			diff = interval - (ts_end-ts_start)
			if diff > 0:
				time.sleep(diff)

	def computeAvgCPU(self, vm):
		for perc in self.cpu_perc[vm]:
			self.NodeToavgCPU[vm] = self.NodeToavgCPU[vm] + perc
		self.NodeToavgCPU[vm] = self.NodeToavgCPU[vm]/len(self.cpu_perc[vm])
	
	def getAvgCPU(self, vm):
		if self.NodeToavgCPU[vm] == 0:
			self.computeAvgCPU(vm)
		return self.NodeToavgCPU[vm]

	def computeAvgTS(self, vm):
		for i in range(0,len(self.ts[vm])-1):	
			self.NodeToavgTS[vm] = self.NodeToavgTS[vm] + (self.ts[vm][i+1] - self.ts[vm][i])
		self.NodeToavgTS[vm] = (self.NodeToavgTS[vm]/len(self.ts[vm]))
	
	def getAvgTS(self, vm):
		if self.NodeToavgTS[vm] == 0:
			self.computeAvgTS(vm)
		return self.NodeToavgTS[vm]

	def computeVarCPU(self, vm):
		if self.NodeToavgCPU[vm] == 0.0:
			self.computeAvgCPU(vm)
		for i in range(0,len(self.cpu_perc[vm])):	
			self.NodeTovarCPU[vm] = self.NodeTovarCPU[vm] + math.pow((self.cpu_perc[vm][i] - self.NodeToavgCPU[vm]), 2)
		self.NodeTovarCPU[vm] = (self.NodeTovarCPU[vm]/(len(self.cpu_perc[vm])-1))

	def getVarCPU(self, vm):
		if self.NodeTovarCPU[vm] == 0.0:
			self.computeVarCPU(vm)
		return self.NodeTovarCPU[vm]

	def computeVarTS(self, vm):
		if self.NodeToavgTS[vm] == 0.0:
			self.computeAvgTS(vm)
		for i in range(0,len(self.ts[vm])-1):	
			self.NodeTovarTS[vm] = self.NodeTovarTS[vm] + math.pow(((self.ts[vm][i+1] - self.ts[vm][i]) - self.NodeToavgTS[vm]), 2)
		self.NodeTovarTS[vm] = (self.NodeTovarTS[vm]/(len(self.ts[vm])-1))

	def getVarTS(self, vm):
		if self.NodeTovarTS[vm] == 0.0:
			self.computeVarTS(vm)
		return self.NodeTovarTS[vm]
		
	def getDEVCPU(self, vm):
		if self.NodeTovarCPU[vm] == 0.0:
			self.computeVarCPU(vm)
		return math.sqrt(self.NodeTovarCPU[vm])
	
	def getDEVTS(self, vm):
		if self.NodeTovarTS[vm] == 0.0:
			self.computeVarTS(vm)
		return math.sqrt(self.NodeTovarTS[vm])	


if __name__ == '__main__':

	data = {'message':'getVMTop', 'vm_list':['Host1']}
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('10.216.32.22', 8888))
	s.send(json.dumps(data))
	result = json.loads(s.recv(1024))
	print result
	s.close()



