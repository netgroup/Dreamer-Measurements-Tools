#!/usr/bin/python

from iperf_nodes import *
from xentop_poller import *
from experiments import *
from experiments_utils import *
from time import sleep

if __name__ == '__main__':

	clean_environment()
	(username, password) = load_conf()
	c1 = iperfClient(["10.216.33.182", username, password])
	s1 = iperfServer(["10.216.33.180", username, password])	
	s1.start()
	first = Experiment(20, c1, s1, ["10.0.3.2", 20, 20, 1, 10],{"10.216.32.22":["Host1"]})
	first.start()
	#sleep(300)
	#second = Experiment(20, c1, s1, ["10.0.3.2", 20, 8, 1, 10],{"10.216.32.22":["Node4"]})
	#second.start()
	#sleep(300)
	#third = Experiment(20, c1, s1, ["10.0.3.2", 20, 12, 1, 10],{"10.216.32.22":["Node4"]})
	#third.start()
	#sleep(300)
	#fourth = Experiment(20, c1, s1, ["10.0.3.2", 20, 16, 1, 10],{"10.216.32.22":["Node4"]})
	#fourth.start()
	#sleep(300)
	#fifth = Experiment(20, c1, s1, ["10.0.3.2", 20, 20, 1, 10],{"10.216.32.22":["Node4"]})
	#fifth.start()	
	s1.close()
	c1.close()	
