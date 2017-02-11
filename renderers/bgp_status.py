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


def render_device(bgp_data):
    template_path = template_dir + 'bgp_status_device.tpl'
    rendered = render_template(bgp_data, template_path)
    return rendered


def render_toc(bgp_dev_names):
    template_path = template_dir + 'bgp_status_toc.tpl'
    rendered = render_template(bgp_dev_names, template_path)
    return rendered


def run(world):
    bgp_dev_names = []
    output_dir = cfg.get('global', 'html_dir') + '/bgp_status/'
    try:
        os.makedirs(output_dir)
    except OSError as exc:  # Python >2.5
        pass

    for dev_name, dev in world.items():
        if 'bgp' in dev:
            bgp_dev_names.append(dev_name)
            data = dev['bgp']
            data.sort(key=lambda session: session['elapsed-time'])
            data.sort(key=lambda session: -1 if session['state'] != 'Established' else 1)
            for session in data:
                session['elapsed-time'] = ago.human(timedelta(seconds=session['elapsed-time']))
            rendered = render_device(data)
            write_file(rendered, output_dir + dev_name + '.html')
    rendered = render_toc(bgp_dev_names)
    write_file(rendered, output_dir + 'index.html')
