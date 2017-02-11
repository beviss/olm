import sys
import datetime
import json
import re
sys.path.insert(0, "..")
import utils
import config as cfg


def dependencies():
    return {'checks': ['find_neighbors'], 'data': ['vlans']}


def run(world):
    mismatch = {}
    processed = set()
    # regexp to recognize '::' port descriptions
    uplink_rexp_pattern = '.*(::[a-z0-9-]+).*'
    uplink_rexp = re.compile(uplink_rexp_pattern)

    for dev_name, dev in world.items():
        # merge vpls data with vlan data
        if 'vpls' in dev:
            for (vpls_id, vpls) in dev['vpls'].items():
                egress = vpls['egress']
                for (vlan_id, iface_id, tagged) in egress:
                    if iface_id not in dev['vlan_mapping']:
                        dev['vlan_mapping'][iface_id] = {}
                    dev['vlan_mapping'][iface_id][vlan_id] = tagged

    all_vlans = {}
    for dev_name, dev in world.items():
        all_vlans.update(dev['vlans'])
        if 'vpls' in dev:
            all_vlans.update(dev['vpls'])
            print dev_name
            print dev['vpls']

    print all_vlans.keys()

    #all_vlans = {816: {'name': 'CORE_MGMT'}}
    for vlan_tag, vlan_data in all_vlans.items():
        real_nodes = set()
        nodes = set()
        adjacencies = {}
        empty_string_count = 1
        for dev_name, dev in world.items():
            adjacency = {}
            vlan_present = False
            if vlan_tag in dev['vlans']:
                vlan_present = True
            if 'vpls' in dev:
                for vpls_id, vpls in dev['vpls'].items():
                    tags = [t[0] for t in vpls['egress']]
                    if vlan_tag in tags:
                        vlan_present = True
                        others = [h.split('.')[0] for h in vpls['peers_hostnames']]
                        print 'OTHERS:', others, vlan_tag
                        for other in others:
                            nodes.add(other)
                            if other in world:
                                real_nodes.add(other)
                            adjacency[other] = 'VPLS'
            for ifid, vlans in dev['vlan_mapping'].items():
                if vlan_tag in vlans:
                    # print dev_name.upper(), 'has vlan', vlan_tag, 'on port',
                    # dev['ifaces'][ifid]['name']
                    if dev['ifaces'][ifid]['descr'].startswith('::'):
                        other = dev['ifaces'][ifid]['descr'][2:]
                    else:
                        other = dev['ifaces'][ifid]['descr']
                    port = dev['ifaces'][ifid]['name']
                    if other in ['""', '']:
                        other = port
                        if other in ['""', '']:
                            other = 'EMPTY_STRING' + str(empty_string_count)
                            empty_string_count += 1
                    nodes.add(other)
                    if other in world:
                        real_nodes.add(other)
                    adjacency[other] = port
            if vlan_present:
                real_nodes.add(dev_name)

            adjacencies[dev_name] = adjacency
        nodes -= real_nodes
        all_nodes = nodes.union(real_nodes)
        for n in all_nodes:
            if n not in adjacencies:
                adjacencies[n] = []
        connectivity_output = {}
        connectivity_output["nodes"] = list(all_nodes)
        connectivity_output["connections"] = adjacencies
        connections_json = json.dumps(connectivity_output)
        line_below_should_be_fixed_and_this_will_trigger_an_exception += 1
        outfile = open('TODO: GET THIS FROM CONFIG' + str(vlan_tag) + '.json', 'w')
        outfile.write(connections_json)
        outfile.close()
        processed = set()
        links = []
        nodes2 = [{'name': n} for n in nodes]
        for n in real_nodes:
            processed.add(n)
            nodes2.append({'name': n})
            for neigh, port in adjacencies[n].items():
                if (not neigh in processed) or (not n in adjacencies[neigh]):
                    neigh_port = '?'  # default
                    if neigh not in real_nodes:  # we dont have access to this neighbor so we dont know
                        neigh_color = 'grey'
                    else:
                        # neighbor has this vlan on his adjacent port
                        if n in adjacencies[neigh]:
                            neigh_color = 'green'
                            neigh_port = adjacencies[neigh][n]
                        else:                       # neighbor doesnt have this vlan on adjacent port
                            neigh_color = 'red'
                    links.append({'endpoints': [n, neigh], 'linkColors': ['green', neigh_color], 'linkLabels': [port, neigh_port]})
        connectivity_output = {}
        connectivity_output["nodes"] = nodes2
        connectivity_output["links"] = links
        connections_json = json.dumps(connectivity_output)
        line_below_should_be_fixed_and_this_will_trigger_an_exception2 += 1
        outfile = open('TODO: GET THIS FROM CONFIG' + str(vlan_tag) + '.json', 'w')
        outfile.write(connections_json)
        outfile.close()
