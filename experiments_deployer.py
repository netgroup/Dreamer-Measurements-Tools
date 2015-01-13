#!/usr/bin/python

from iperf_nodes import *
from xentop_poller import *
from experiments import *
from experiments_utils import *
from time import sleep

if __name__ == '__main__':

	clean_environment()
	(username, password) = load_conf()
	clis = []
	sers = []
	c1 = iperfClient(["62.40.110.52", username, password, "10.0.9.1"])
	clis.append(c1)
	s1 = iperfServer(["62.40.110.20", username, password])	
	sers.append(s1)
	first = ZabbixExperiment(1, clis, sers, [5, 50, 40, 2],['DREAMER-TESTBED-OSHI-PE-31-CPU30'])
	first.start()
	for server in sers:
		server.close()
	for client in clis:
		client.close()	
