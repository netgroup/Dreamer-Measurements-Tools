#!/usr/bin/python

from getpass import getpass
from pyzabbix import ZabbixAPI
import time
import socket
import json
import time
import math
from threading import Thread
from collections import defaultdict
import re
import string
import os

class Poller(object):
	
	def __init__(self, length, interval, vms, meas_server, delay):
		self.cpu_perc = defaultdict(list)
		self.ts = defaultdict(list)
		self.thread = Thread(target = self.getVMsCPU, args=(length, interval, vms, meas_server, delay))
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

	def getVMsCPU(self, length, interval, vm, xenaddr, delay):
		raise NotImplementedError("Abstract Method")

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


class XentopPoller(Poller):
	
	XENPORT = 8888
	MSIZE = 1024
	KEYCPU = 'cpu_perc'
	KEYTS = 'timestamp'

	def __init__(self, length, interval, vms, xenaddr, delay):
		Poller.__init__(self, length, interval, vms, xenaddr, delay)

	def getVMsCPU(self, length, interval, vms, xenaddr, delay):
		request = {'message':'getVMTop', 'vm_list':vms}
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

class ZabbixPoller(Poller):
	
	KEYITEMID='itemid'
	KEYNAME='name'
	KEYSERVER='server'
	KEYUSERNAME='username'
	KEYPASSWORD='password'
	KEYCPU='lastvalue'
	KEYTS='lastclock'
	CONF='.zabbix.conf'

	def __init__(self, length, interval, vms, delay):
		Poller.__init__(self, length, interval, vms, None, delay)
		self.load_conf()
		self.zapi = ZabbixAPI(self.ZABBIX_SERVER)
		self.zapi.login(self.USERNAME, self.PASSWORD)
		self.map_id_to_name = {}
		self.getVMsID(vms)

	def load_conf(self):
		if os.path.exists(self.CONF) == False:
			print "Error Create Configuration File %s" % self.CONF
			sys.exit(-2)
		conf = open(self.CONF)
		json_data = json.load(conf)
		self.ZABBIX_SERVER = json_data[self.KEYSERVER]
		self.USERNAME = json_data[self.KEYUSERNAME]
		self.PASSWORD = json_data[self.KEYPASSWORD]
		conf.close()

	def getVMsID(self, vms):
		for vm in vms:
			item = self.zapi.item.get(filter={self.KEYNAME:vm})
			self.map_id_to_name[item[0][self.KEYITEMID]]=vm

	def getVMsCPU(self, length, interval, vms, xenaddr, delay):
		i = 0
		print "Zabbix Poller discards first \"delay\" values"
		last_ts = 0
		# Discard first "delay" values
		while (delay >= 0):
			ts_start = time.time()
			items = self.zapi.item.get(filter={self.KEYNAME:vms})
			ts_end = time.time()
			for item in items:
					if item:
						ts_value = float(item[self.KEYTS])			
						if ts_value != last_ts:
							delay = delay - 1
							last_ts = ts_value
						break
			ts_end = time.time()
			diff = 2 - (ts_end-ts_start)
			if diff > 0:
				time.sleep(diff)
		print "Zabbix Poller takes data"
		# Take data
		while i < (length * len(vms)):
			ts_start = time.time()
			items = self.zapi.item.get(filter={self.KEYNAME:vms})
			ts_end = time.time()
			for item in items:
					if item:
						vm = self.map_id_to_name[item[self.KEYITEMID]]
						ts_value = float(item[self.KEYTS])
						if ts_value not in self.ts[vm]:
							self.cpu_perc[vm].append(float(item[self.KEYCPU]))
							self.ts[vm].append(ts_value)
							i = i + 1
			ts_end = time.time()
			diff = 2 - (ts_end-ts_start)
			if diff > 0:
				time.sleep(diff)	

if __name__ == '__main__':
	poller = ZabbixPoller(10, 30, ['DREAMER-TESTBED-OSHI-PE-23'], 1)
	poller.start()
	poller.join()
	for key, cpu_data in poller.cpu_perc.iteritems():
		print "%s -> CPU:%s" %(key, cpu_data)
	for key, ts_data in poller.ts.iteritems():
		print "%s -> TS:%s" %(key, ts_data)





