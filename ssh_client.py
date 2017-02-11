import time
import paramiko
from collections import defaultdict

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

debug = False


def debug_print(*args):
    if not debug:
        return
    for arg in args:
        print arg,
    print '\n',


def get_ssh_output(channel):
    result = ""
    receive_chunk_length = 100
    received_bytes = receive_chunk_length
    chunk = ""
    while not chunk.endswith(">"):
        debug_print('chunk received: len = ', received_bytes)
        debug_print('chunk:', chunk + '|')
        chunk = channel.recv(receive_chunk_length)
        received_bytes = len(chunk)
        result = result + chunk
        chunk = chunk.strip()
    return result


def ssh_command(hostname, command, username, password, quirks=None):
    ssh.connect(hostname, username=username, password=password, look_for_keys=False, allow_agent=False)
    chan = ssh.invoke_shell()
    prompt = get_ssh_output(chan)
    if quirks == 'brocade':
        chan.send('terminal length 0\n')
        prompt = get_ssh_output(chan)
    elif quirks == 'juniper':
        chan.send('set cli complete-on-space off\n')
        prompt = get_ssh_output(chan)
        chan.send('set cli screen-length 0\n')
        prompt = get_ssh_output(chan)
        chan.send('set cli screen-width 0\n')
        prompt = get_ssh_output(chan)
    debug_print(prompt)
    chan.send(command + '\n')
    debug_print('command sent')
    output = get_ssh_output(chan)
    ssh.close()
    return output
