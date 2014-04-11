#!/usr/bin/python

import sys
import paramiko
import cmd
import re
from subprocess import Popen
from threading import Thread
from time import sleep
import os

class iperfNode(object):

	def __init__(self, host, user, pwd):
		self.host = host
		self.user = user
		self.pwd = pwd
		self.chan = None
		self.conn = None
		self.process = None
		path_log = "./log/%s.log" % host
		if os.path.exists(path_log):
			os.remove(path_log)
		self.log = open( path_log, "a")
		self.STOP = False
		self.t_connect()

	def t_connect(self):    
		self.conn_thread = Thread( target=self.connect)
		self.conn_thread.start()
		self.conn_thread.join()

	def connect(self):
		self.conn = paramiko.SSHClient()
		self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.conn.connect(self.host,username=self.user, password=self.pwd)
		self.chan = self.conn.invoke_shell()
		self.wait_command('',False) 

	def run(self, command, verbose=True):
		buff = ''
		self.chan.send(command+"\r")
		buff = self.wait_command(command, verbose)
		return buff

	def exe(self, command):
		buff = ''
		stdin, stdout, stderr = self.conn.exec_command(command)
		stdin.close()
		for line in stdout.read().splitlines():
			buff+= line+'\n'
		return buff    

	def wait_command(self,command, verbose):
		buff = ''
		i = 0
		s = re.compile('[^#]# ')
		u = re.compile('[$] ')  
		while not u.search(buff) and not s.search(buff) and self.STOP == False:
			resp = self.chan.recv(9999)
			if (verbose):
				self.log.write(resp)
			buff += resp
		if (verbose):
			self.log.write("\n")
		return buff

	def close(self):
		self.STOP = True
		if self.conn != None:
			self.conn.close()
			if self.process:
				self.process.terminate()
		self.log.close()

class iperfClient(iperfNode):

	UDP = "-u"
	DGRAMSIZE= "-l 1000"
	BUFFSIZE= "-w 256k"	

	def __init__(self, params):
		iperfNode.__init__(self, params[0], params[1], params[2])
		self.op_thread = None

	def start(self, server, length, rate):
		server = "-c %s" % server
		length = "-t %s" % length
		rate = "-b %sm" % rate
		params = "iperf %s %s %s %s %s %s" % (server, self.UDP, rate, self.DGRAMSIZE, length, self.BUFFSIZE)
		self.op_thread = Thread(target = self.iperf, args=(params,))
		self.op_thread.start()
	
	def join(self):		
		self.op_thread.join()

	def iperf(self, params):
		self.log.write("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
		iperfNode.run(self, params, True)


class iperfServer(iperfNode):
	
	UDP = "-u"
	DGRAMSIZE= "-l 1000"
	BUFFSIZE= "-w 256k"	

	def __init__(self, params):
		iperfNode.__init__(self, params[0], params[1], params[2])
		self.op_thread = None

	def start(self):
		params = "iperf -s %s %s %s" % (self.UDP, self.DGRAMSIZE, self.BUFFSIZE)
		self.op_thread = Thread(target = self.iperf, args=(params,))
		self.op_thread.start()
		

	def iperf(self, params):
		iperfNode.run(self, params, True)
	
	def close(self):
		iperfNode.close(self)
		self.op_thread.join()