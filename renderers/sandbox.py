import sys
import os
import re
import datetime
import jinja2
import pprint
sys.path.insert(0, "..")
import config as cfg
import ago
from datetime import timedelta


def atoi(text):
    return int(text) if text.isdigit() else text


def render_template(result, template_filename):
    template_loader = jinja2.FileSystemLoader(searchpath="/")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_filename)
    datetime
    rendered = template.render({'result': result, 'date': datetime.datetime.now().isoformat()})
    return rendered


def render_and_write_template(result, template_filename, output_filename):
    rendered = render_template(result, template_filename)
    write_file(output_filename)


def write_file(text, filename):
    output_file = open(filename, 'w')
    output_file.write(text)
    output_file.close()

template_dir = cfg.get('global', 'install_dir') + '/renderers/'

def run(world):
    for dev_name, data in world.items():
        print dev_name
        for entry in data['mac_table']:
            mac = entry['mac']
            for dev_name2, data2 in world.items():
                for iface in data2['ifaces'].values():
                    #print 'checking', repr(mac), 'against', repr(iface['mac'])
                    if iface['mac'] == mac:
                        print dev_name, 'has', dev_name2, 'on iface', data['ifaces'][entry['ifIndex']]['name']
