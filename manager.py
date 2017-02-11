#!/usr/bin/env python

import sys
import pprint
import threading
from Queue import Queue

from snmpwalk import snmpwalk
import snmpwalk as snmp
import config
import oids
import devices
import cache
import argparse
import logging as log
import traceback

sys.path.insert(0, 'checks')
sys.path.insert(0, 'data')
sys.path.insert(0, 'renderers')

log.basicConfig(level=log.DEBUG)


parser = argparse.ArgumentParser(description=sys.argv[0])
parser.add_argument('config', metavar='c', nargs='?', type=str, help='configuration file path', default='config.yaml')
parser.add_argument('-m', '--disable-cache', help='disable reading saved cache', default=False, action='store_true')
parser.add_argument('-t', '--thread-count', help='data plugins thread count', type=int, default=1)
args = parser.parse_args()

print args

config.init(args.config)

cfg = config.cfg

if args.disable_cache:
    cfg.set('global:read_cache', False)
    cfg.set('global:write_cache', False)

check_plugins = cfg.get('global:checks_enabled')
data_plugins = cfg.get('global:data_enabled')
render_plugins = cfg.get('global:renderers_enabled')

num_threads = args.thread_count
world = {}

exc_file = open('exceptions', 'w')


def get_module_from_thread(module_name):
    return globals()[module_name]

# this is a thread worker, member of a thread pool
# one task is one device


class Worker(threading.Thread):

    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            dev = self.task_queue.get()
            if dev is None:
                self.task_queue.task_done()
                break
            for data_plugin in data_plugin_modules:
                log.debug('   ... Running data plugin {0} for device {1}'.format(
                    data_plugin.__name__, dev))
                key = data_plugin.key()
                try:
                    data = data_plugin.run(dev)
                    world[dev.name][key] = data
                except Exception as e:
                    traceback.print_exc()
                    traceback.print_exc(None, exc_file)
            self.task_queue.task_done()

cache.init()

# initialize data tree
devs = devices.get_dev_list()
print 'Devices count:', len(devs)
for d in devs:
    print d.hostname, d.model
for dev in devs:
    world[dev.name] = {'dev': dev}

data_plugin_modules = []

for data_plugin_name in data_plugins:
    print '   ... Importing data plugin', data_plugin_name
    data_plugin_modules.append(__import__(data_plugin_name))

task_queue = Queue()
workers = [Worker(task_queue) for _ in range(num_threads)]

for dev in devs:
    task_queue.put(dev)

task_queue.join()

# stop the threads
for _ in range(num_threads):
    task_queue.put(None)
task_queue.join()

if cfg.get('global:write_cache'):
    cache.dump(cache.cache)

print '... Running checks'
for check_plugin_name in check_plugins:
    print '   ... Running check', check_plugin_name
    plugin = __import__(check_plugin_name)
    try:
        plugin.run(world)
    except Exception as e:
        print e

print '... Running renderers'
for render_plugin_name in render_plugins:
    print '   ... Running renderer', render_plugin_name
    plugin = __import__(render_plugin_name)
    plugin.run(world)


print 'Stats:'
pp = pprint.PrettyPrinter(indent=4)
for dev in snmp.stats:
    print str(dev)
    pp.pprint(snmp.stats[dev])
