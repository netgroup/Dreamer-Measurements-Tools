![Alt text](repo_data/dreamer-logo.png "Optional title")

Dreamer-Measurements-Tools
==========================

Measurements Tools For Dreamer Project (GÉANT Open Call)

Using this tool you can run iperf experiment on OSHI testbed and collect CPU load
of your VMs thanks to xentop tool.

License
=======

This sofware is licensed under the Apache License, Version 2.0.

Information can be found here:
 [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).

Tips
==============

See [Dreamer-Measurement-Tools How-To](http://netgroup.uniroma2.it/twiki/bin/view/Oshi/OshiExperimentsHowto#MeasurementTools)

Measurement Tools Dependencies
=============================

1) paramiko (pip)

Usage
=====

Example of usage Measurement Tools

		if __name__ == '__main__':
			# Delete Log files and other clean
			clean_environment()
			# Load username and password
			(username, password) = load_conf()
			# Create Iperf Client and Server
			c1 = iperfClient(["10.216.33.182", username, password])
			s1 = iperfServer(["10.216.33.180", username, password])	
			# Start the Iperf Server
			s1.start()
			# Create an experiment: 20 Round, Client, Server, Params (Server IP, Round length, Iperf Rate, Initial Delay), Map VMtoXen
			first = Experiment(20, c1, s1, ["10.0.3.2", 20, 20, 1, 10],{"10.216.32.22":["Host1"]})
			# Start the experiment
			first.start()
