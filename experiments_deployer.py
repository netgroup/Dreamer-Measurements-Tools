#!/usr/bin/python

from iperf_nodes import *
from xentop_poller import *
from experiments import *
from experiments_utils import *

if __name__ == '__main__':

	(username, password) = load_conf()
	c1 = iperfClient(["10.216.33.181", username, password])
	s1 = iperfServer(["10.216.33.180", username, password])	
	s1.start()
	first = Experiment(5, c1, s1, ["10.0.9.2","5","4"],{"10.216.32.22":["Node4","EUH01"])
	first.start()
	s1.close()
	c1.close()	
