import templates
import config as cfg


def run(world):
    result = []
    for name, data in world.items():
        print name
        dev = data['dev'].name
        if 'mac_table' in data:
            if len(data['mac_table']) > 0:
                for entry in data['mac_table']:
                    try:
                        ifIndex = int(entry['ifIndex'])
                    except:
                        ifIndex = None
                    if ifIndex in data['ifaces']:
                        ifName = data['ifaces'][ifIndex]['name']
                    else:
                        ifName = '??' + str(ifIndex)
                    vlan = int(entry['vlan'])
                    if 'vlans' in data:
                        if vlan in data['vlans']:
                            vlan = data['vlans'][vlan]['name'] + ' (' + str(vlan) + ')'
                    result.append((dev, ifName, vlan, entry['mac']))
    template_dir = cfg.get('global', 'install_dir') + '/checks/print_mac_table'
    html_dir = cfg.get('global', 'html_dir')
    templates.render_template(result, template_dir + '/print_mac_table.tpl', html_dir + '/mac_table.html')
