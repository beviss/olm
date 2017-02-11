#!/usr/bin/env python
import yaml
import time
import re

import ssh_client

with open('config.yaml', 'r') as secrets_file:
    config = yaml.load(secrets_file)
    username = config['user']
    password = config['password']
    address = config['address']
    interface = config['interface']
    interval = int(config['interval'])
    logfilename = config['logfile']

logfile = open(logfilename, 'a')

tx_regexp = re.compile(r'Laser output power +:')
rx_regexp = re.compile(r'Receiver signal average optical power +:')

while True:
    command = 'show interfaces diagnostics optics ' + interface
    output = ssh_client.ssh_command(address, command, username, password, quirks='juniper')
    print 'Received output:'
    print output
    print '=========================================='
    output = output.splitlines()
    timestamp = str(int(time.time()))
    for line in output:
        if tx_regexp.search(line):
            tx_power = line.split()[7]
            logfile.write(timestamp + ' tx ' + tx_power + '\n')
            logfile.flush()
        if rx_regexp.search(line):
            rx_power = line.split()[9]
            logfile.write(timestamp + ' rx ' + rx_power + '\n')
            logfile.flush()
    time.sleep(interval)
