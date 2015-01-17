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

2) pyzabbix (pip)

Usage
=====

Example of usage Measurement Tools (OFELIA)

                if __name__ == '__main__':
                        # Delete Log files and other clean
                        clean_environment()
                        # Load username and password
                        (username, password) = load_conf()
                        # Create Iperf Client and Server
                        clis = []
                        sers = []
                        c1 = iperfClient([IPc, username, password, "10.0.9.1"])
                        clis.append(c1)
                        s1 = iperfServer([IPs, username, password])        
                        sers.append(s1)
                        # Create an experiment: 1 Round, Clients, Servers, Params (Round length, Iperf Rate, sample interval Initial Delay), Map VMtoXen
                        first = XentopExperiment(1, clis, sers, [5, 50, 40, 2], {XENIP:[HOST1, HOST2]})
                        # Start the experiment
                        first.start()
                        for server in sers:
                            server.close()
                        for client in clis:
                            client.close()
                        
Example of usage Measurement Tools (GOFF)

                if __name__ == '__main__':
                        clean_environment()
                        (username, password) = load_conf()
                        clis = []
                        sers = []
                        c1 = iperfClient([IPc, username, password, "10.0.9.1"])
                        clis.append(c1)
                        s1 = iperfServer([IPs, username, password])        
                        sers.append(s1)
                        first = ZabbixExperiment(1, clis, sers, [5, 50, 40, 2],[HOST2, HOST1])
                        first.start()
                        for server in sers:
                            server.close()
                        for client in clis:
                            client.close()       
