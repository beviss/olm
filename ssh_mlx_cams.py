import time
import paramiko
import getpass
import requests
import yaml
from collections import defaultdict

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#password = getpass.getpass('password: ')
with open('secrets.yaml', 'r') as secrets_file:
    secrets = yaml.load(secrets_file)
    username = secrets[0]['user']
    password = secrets[0]['password']
influxdb_url = 'TODO: GET THIS FROM CONFIG'
max_macs = 2048


def get_ssh_output(channel):
    result = ""
    receive_chunk_length = 100
    received_bytes = receive_chunk_length
    chunk = ""
    while not chunk.endswith(">"):
        print "chunk received: len = ", received_bytes
        print "chunk:", chunk
        chunk = channel.recv(receive_chunk_length)
        received_bytes = len(chunk)
        result = result + chunk
        chunk.strip()
    return result


def ssh_command(hostname, command, username, password):
    ssh.connect(hostname, username=username, password=password, look_for_keys=False, allow_agent=False)
    chan = ssh.invoke_shell()
    prompt = get_ssh_output(chan)
    chan.send('terminal length 0\n')
    prompt = get_ssh_output(chan)
    print prompt
    chan.send(command + '\n')
    output = get_ssh_output(chan)
    ssh.close()
    return output


times_mactable = 15
sleep_time = 60
times = times_mactable

while True:
    hostnames = ['TODO', 'GET', 'THIS FROM CONFIG']
    hostname_limit = None  # useful when debugging
    for hostname in hostnames[:hostname_limit]:
        timestamp = str(int(time.time()))
        output = ssh_command(
            hostname, 'show mpls vpls summary', username, password)
        output = output.splitlines()
        for line in output:
            if 'Maximum VPLS mac entries allowed' in line:
                rec = line.split()
                max_macs = rec[5].replace(',', '')
                macs_present = rec[8]
        print output
        print max_macs, macs_present
        data = 'cam,dev={0},type=absolute value={1} {2}'.format(hostname, macs_present, timestamp)
        r = requests.post(influxdb_url, data=data)
        print r.text
        print r.status_code
        macs_percent = (float(macs_present) / float(max_macs)) * 100
        data = 'cam,dev={0},type=percent value={1} {2}'.format(hostname, macs_percent, timestamp)
        requests.post(influxdb_url, data=data)
        print r.text
        print r.status_code

    if times == times_mactable:
        times = 0
        for hostname in hostnames[:hostname_limit]:
            output = ssh_command(hostname, 'show mac-address vpls', username, password)
            print output
            output = output.splitlines()
            mac_count = defaultdict(lambda: 0)
            for line in output[5:-1]:  # skip 5 line header
                rec = line.split()
                vpls_id = rec[0].strip()
                mac_count[vpls_id] += 1
            for vpls, count in mac_count.items():
                data = 'cam,dev={0},vpls={1}  value={2} {3}'.format(hostname, vpls, count, timestamp)
                requests.post(influxdb_url, data=data)

    times += 1
    print "Times counter: ", times
    print "Sleeping", sleep_time, "seconds..."
    time.sleep(sleep_time)
