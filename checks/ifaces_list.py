import sys
import os
import re
import datetime
import jinja2
import pprint
sys.path.insert(0, "..")
import config as cfg


def atoi(text):
    return int(text) if text.isdigit() else text


def render_template(result, template_filename, output_filename):
    template_loader = jinja2.FileSystemLoader(searchpath="/")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_filename)
    rendered = template.render({'result': result, 'date': datetime.datetime.now().isoformat()})
    output_file = open(output_filename, 'w')
    output_file.write(rendered)
    output_file.close()


def run(world):
    pp = pprint.PrettyPrinter(indent=4)
    result = {}
    # rewrite juniper vlan_mapping to be indexed by ifindex, not iface name
    for dev in world:
        if len(world[dev]['vlan_mapping'].keys()) > 0:
            if type(world[dev]['vlan_mapping'].keys()[0]) == str:  # correct juniper ifnames
                new_map = {}
                # i - interface name, m - { vlan : tagness }
                for (i, m) in world[dev]['vlan_mapping'].items():
                    ifs = [(x, y) for (x, y) in world[dev]['ifaces'].items() if y['name'] == i]  # x - ifIndex, y - iface_obj
                    if len(ifs) == 1:
                        new_map[ifs[0][0]] = m
                world[dev]['vlan_mapping'] = new_map
    group_by_linecard = False
    group_by_linecard_success = False
    templates = [('dokuwiki', 'doku'), ('CSV', 'csv'), ('HTML', 'html')]
    template_dir = cfg.get('global', 'install_dir') + '/checks'
    html_dir = cfg.get('global', 'html_dir') + '/ifaces_list'
    master_list = "<html><table>"
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
    for dev in sorted(world.keys()):
        print
        print dev.upper()
        devname = dev
        dev = world[dev]
        if group_by_linecard:
            ports = {}
        else:
            ports = []
        if 'vpls' in dev:
            for (vpls_tag, vpls) in dev['vpls'].items():
                for (egress_vlan, iface_id, tagged) in vpls['egress']:
                    if not iface_id in dev['vlan_mapping']:
                        dev['vlan_mapping'][iface_id] = {}
                    dev['vlan_mapping'][iface_id][egress_vlan] = tagged
                    dev['vlans'][egress_vlan] = {'name': vpls['name']}
        for ifIndex in dev['ifaces']:
            print dev['ifaces'][ifIndex]['name'], dev['ifaces'][ifIndex]['type']
            if not dev['ifaces'][ifIndex]['type'] in ['ethernetCsmacd', 'ieee8023adLag']:
                continue
            port = {}
            port['name'] = dev['ifaces'][ifIndex]['name']
            port['descr'] = dev['ifaces'][ifIndex]['descr']
            port['up'] = dev['ifaces'][ifIndex]['up']
            vlans = []
            if len(dev['vlans']) > 0 and ifIndex in dev['vlan_mapping']:
                for (vlan, tagged) in dev["vlan_mapping"][ifIndex].items():
                    if vlan in dev['vlans']:
                        vlans.append((vlan, dev['vlans'][vlan]['name'], tagged))
                    else:
                        vlans.append((vlan, 'NAME?', tagged))
                port['vlans'] = vlans
            if group_by_linecard:
                m = re.match('(^[A-Z])([0-9]+$)', port['name'])
                if m:  # HP?
                    card_name = m.group(1)
                    port_number = int(m.group(2))
                else:
                    m = re.match('(^(x|g)e-\d/\d/)([0-9]+$)', port['name'])
                    if m:  # Juniper?
                        card_name = m.group(1)
                        print m.groups
                        port_number = int(m.group(3))
                if m:
                    if card_name not in ports:
                        ports[card_name] = []
                    port['name'] = port_number
                    ports[card_name].append(port)
                else:
                    ports['invalid'] = port
                print ports.keys()
            else:
                ports.append(port)
                ports.sort(key=lambda x: [atoi(y)
                                          for y in re.split('(\d+)', x['name'])])
        result[devname] = ports
        master_list += '<tr><td>' + devname + '</td>'
        for tpl_name, tpl_code in templates:
            template_filename = template_dir + '/ifaces_list_' + tpl_code + '.tpl'
            html_filename = devname + '.' + tpl_code
            render_template({devname: ports}, template_filename,
                            html_dir + '/' + html_filename)
            master_list += '<td><a href=' + html_filename + '>' + tpl_name + '</a></td>'
        if group_by_linecard_success:
            render_template({devname: ports}, template_dir + '/ifaces_list_dokuczyki.tpl', html_dir + '/' + devname + '.dokuczyki')
        master_list += '</tr>\n'
    generation_date = datetime.datetime.now().isoformat()
    master_list += '</table><br>Generated at ' + generation_date + '</html>'
    master_list_filename = html_dir + '/index.html'
    master_list_file = open(master_list_filename, 'w')
    master_list_file.write(master_list)
